"""Validate metadata and renamed projects; exercise actual KiCad DRC/ERC rules."""
from pathlib import Path
import argparse,json,re,shutil,subprocess,tempfile,uuid

ROOT=Path(__file__).resolve().parents[1]
NAMES=('jlc-2layer-1oz-prototype','jlc-4layer-1oz-prototype')

def structure():
    result=[]
    for name in NAMES:
        folder=ROOT/'templates'/name
        pro=json.loads((folder/(name+'.kicad_pro')).read_text(encoding='utf-8'))
        pcb=(folder/(name+'.kicad_pcb')).read_text(encoding='utf-8')
        count=2 if '2layer' in name else 4
        assert len(re.findall(r'^\s*\(\d+ "[^"\n]+\.Cu" signal\)',pcb,re.M))==count
        assert not re.search(r'^\s*\((?:footprint|segment|via|zone|gr_\w+)\b',pcb,re.M)
        assert pro['board']['design_settings']['drc_exclusions']==[]
        assert not pro['net_settings']['netclass_patterns']
        assert not pro['net_settings']['netclass_assignments']
        assert not pro['sheets']
        assert not any(v=='ignore' for v in pro['board']['design_settings']['rule_severities'].values())
        assert pro['net_settings']['classes'][0]['clearance']==.127
        assert (folder/(name+'.kicad_sch')).exists()
        assert '<title>' in (folder/'meta/info.html').read_text(encoding='utf-8')
        assert (folder/'RULES.md').exists()
        for path in folder.rglob('*'):
            assert path.name not in ('.git','.history') and not path.name.endswith(('.lck','.kicad_prl'))
            if path.is_file():
                s=path.read_text(encoding='utf-8')
                assert not re.search(r'[CD]:[\\/]|Project FOC|FOC_Project|100\.68\.',s),path
        result.append({'template':name,'structure':'passed','copper_layers':count})
    return result

def uid():return str(uuid.uuid4())

def outline():
    points=((100,100),(125,100),(125,125),(100,125))
    return '\n'.join(f'(gr_line (start {a} {b}) (end {c} {d}) (stroke (width 0.05) (type default)) (layer "Edge.Cuts") (uuid "{uid()}"))' for (a,b),(c,d) in zip(points,points[1:]+points[:1]))

def track(width,layer='F.Cu',y=105.,net='SIGNAL_A'):
    return f'(segment (start 105 {y}) (end 108 {y}) (width {width}) (layer "{layer}") (net "{net}") (uuid "{uid()}"))'

def via(diameter,drill,x=110.,y=110.):
    return f'(via (at {x} {y}) (size {diameter}) (drill {drill}) (layers "F.Cu" "B.Cu") (net "SIGNAL_A") (uuid "{uid()}"))'

def native(cli,summary):
    with tempfile.TemporaryDirectory(prefix='kicad-jlc-templates-') as work:
        work=Path(work)
        for template in summary:
            name=template['template'];src=ROOT/'templates'/name;count=template['copper_layers']
            dst=work/name;dst.mkdir()
            renamed='RenamedProject'
            for ext in ('kicad_pro','kicad_dru','kicad_sch'):
                shutil.copyfile(src/(name+'.'+ext),dst/(renamed+'.'+ext))
            base=(src/(name+'.kicad_pcb')).read_text(encoding='utf-8')
            def check(label,items,expected):
                board=dst/(renamed+'.kicad_pcb')
                i=base.rfind(')');board.write_text(base[:i]+outline()+'\n'+items+'\n'+base[i:],encoding='utf-8')
                report=dst/(label+'.json')
                proc=subprocess.run([cli,'pcb','drc','--format','json','--all-track-errors','--refill-zones','-o',str(report),str(board)],capture_output=True,text=True,encoding='utf-8',errors='replace')
                assert proc.returncode==0,proc.stdout+proc.stderr
                r=json.loads(report.read_text(encoding='utf-8'))
                found={v['type'] for v in r['violations']}
                if not expected:assert not r['violations'] and not r['unconnected_items'],r
                else:assert all(set(item.split('|'))&found for item in expected),(label,expected,found)
                print(name+': '+label+' passed',flush=True)
                return {'case':label,'expected':expected,'detected':sorted(found),'result':'passed'}
            diameter=.5 if count==2 else .45;drill=.3 if count==2 else .2
            cases=[check('empty_project_with_outline','',[])]
            cases.append(check('narrow_outer_track',track(.1),['track_width']))
            if count==4:cases.append(check('narrow_inner_track',track(.1,'In1.Cu'),['track_width']))
            cases.append(check('small_via_drill',via(diameter,.15),['drill_out_of_range']))
            cases.append(check('small_via_outer',via(.45 if count==2 else .35,drill),['via_diameter']))
            cases.append(check('small_annular_ring',via(.5 if count==2 else .4,.4 if count==2 else .3),['annular_width']))
            cases.append(check('small_track_clearance',track(.2)+track(.2,y=105.3,net='SIGNAL_B'),['clearance']))
            cases.append(check('small_via_hole_clearance',via(diameter,drill)+via(diameter,drill,x=110.+drill+.24),['hole_to_hole']))
            pad=f'''(footprint "ValidationPad" (layer "F.Cu") (at 110 110) (uuid "{uid()}")
              (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu" "F.Mask" "F.Paste") (net "SIGNAL_A") (uuid "{uid()}")))
              (gr_line (start 109.5 110.7) (end 110.5 110.7) (stroke (width 0.15) (type default)) (layer "F.SilkS") (uuid "{uid()}"))'''
            cases.append(check('small_silkscreen_gap',pad,['silk_overlap|silk_over_copper']))
            text=f'(gr_text "TEST" (at 110 110) (layer "F.SilkS") (uuid "{uid()}") (effects (font (size 0.5 0.5) (thickness 0.1))))'
            cases.append(check('small_silkscreen_text',text,['text_height','text_thickness']))
            erc=dst/'erc.json'
            proc=subprocess.run([cli,'sch','erc','--format','json','-o',str(erc),str(dst/(renamed+'.kicad_sch'))],capture_output=True,text=True,encoding='utf-8',errors='replace')
            assert proc.returncode==0,proc.stdout+proc.stderr
            er=json.loads(erc.read_text(encoding='utf-8'))
            assert not er.get('violations'),er
            template.update(native_cases=cases,empty_schematic_erc='passed',renamed_project='passed')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-cli',default=shutil.which('kicad-cli'))
    parser.add_argument('--structure-only',action='store_true')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    summary=structure()
    if not args.structure_only:
        assert args.kicad_cli,'Pass --kicad-cli /path/to/kicad-cli or use --structure-only explicitly'
        summary=native(args.kicad_cli,summary)
    result={'structure_only':args.structure_only,'templates':summary}
    if not args.structure_only:
        version=subprocess.run([args.kicad_cli,'version'],capture_output=True,text=True,check=True)
        result['kicad_version']=version.stdout.strip()
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
