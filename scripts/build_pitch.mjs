// Author with @oai/artifact-tool. Invoke using a Node installation with that package.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
try {
const root=process.env.AEGIS_ROOT||path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const packagePath=process.env.ARTIFACT_TOOL_MODULE;
const {Presentation,PresentationFile}=await import(packagePath?pathToFileURL(packagePath).href:'@oai/artifact-tool');
const data=JSON.parse(await fs.readFile(path.join(root,'presentation/pitch_data.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const INK='#0C1822',WHITE='#E8EFF2',MINT='#55CCB0',GOLD='#D8B76E',MUTED='#AAC1CD';
function text(slide,value,left,top,width,height,size=30,color=WHITE,bold=false,font='Aptos'){
  const s=slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
  s.text=value;s.text.style={fontFamily:font,fontSize:size,color,bold};return s;
}
for(const [i,d] of data.entries()){
  const slide=p.slides.add();slide.background.fill=INK;
  text(slide,'QUANTUM-X / SERENDIB UNIVERSITY ENDOWMENT',65,38,1145,30,16,MINT,true);
  text(slide,d.title,65,99,1140,100,i===0?68:43,WHITE,false,'Georgia');
  const evidence=Boolean(d.chart||d.table);
  text(slide,d.body,65,211,evidence?1050:1090,evidence?120:300,evidence?25:35,MUTED);
  if(d.chart){
    const chart=slide.charts.add('bar',{position:{left:65,top:348,width:1140,height:292},categories:d.chart.categories,
      series:d.chart.series.map((s,j)=>({...s,values:s.values.map(v=>Number(v.toFixed(6))),fill:j===0?MINT:GOLD})),hasLegend:d.chart.series.length>1,
      barOptions:{direction:'column',grouping:'clustered',gapWidth:90},
      chartFill:INK,plotAreaFill:INK,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},
      xAxis:{textStyle:{typeface:'Aptos',fontSize:16,color:WHITE}},
      yAxis:{textStyle:{typeface:'Aptos',fontSize:16,color:WHITE},numberFormatCode:'0.0',majorGridlines:{fill:'#29404C',width:1,style:'solid'}},
      legend:{textStyle:{typeface:'Aptos',fontSize:17,color:WHITE}},
      dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:'Aptos',fontSize:16,color:WHITE},numberFormatCode:'0.0'}});
  }
  if(d.table){
    const table=slide.tables.add({rows:d.table.length,columns:d.table[0].length,left:65,top:346,width:1140,height:292,values:d.table,
      columnWidths:d.table[0].length===4?[480,220,220,220]:[360,200,180,180,220]});
    table.borders.assign({style:'solid',fill:'#34505E',width:1});
    for(let row=0;row<d.table.length;row++)for(let col=0;col<d.table[0].length;col++){
      const cell=table.getCell(row,col);cell.fill=row===0?'#224553':row%2?'#132633':INK;
      cell.text.style={fontFamily:'Aptos',fontSize:19,color:WHITE,bold:row===0};
    }
  }
  text(slide,`${String(i+1).padStart(2,'0')} / ${data.length}    ·    DATA THROUGH 30 SEP 2026    ·    PROPOSAL PENDING TEAM REVIEW`,65,675,1140,24,14,MINT);
  slide.speakerNotes.text=`Rehearsal timing: ${d.seconds} seconds.\n${d.notes}\nEvidence: outputs/results/summary.json and outputs/tables; assumptions and method sources: documentation/Sources.md. OpenAI Codex assisted; independent human review pending.`;
}
const build=process.env.AEGIS_DECK_BUILD||path.join(root,'.deck_build');await fs.mkdir(build,{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
for(const [i,slide] of p.slides.items.entries()){
  const png=await p.export({slide,format:'png',scale:1});await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
if(process.env.AEGIS_SKILL_DIR){
 const sk=process.env.AEGIS_SKILL_DIR;
 const {finalizePresentation}=await import(pathToFileURL(path.join(sk,'container_tools/artifact_tool_utils.mjs')).href);
 await finalizePresentation({workspaceDir:path.dirname(root),candidatePath:path.join(build,'candidate.pptx'),finalPath:path.join(root,'presentation/Final_Pitch.pptx'),
   pythonExecutable:process.env.AEGIS_RUNTIME_PYTHON,integrityValidatorPath:path.join(sk,'container_tools/inspect_presentation_package_integrity.py'),
   layoutValidatorPath:path.join(sk,'container_tools/inspect_presentation_layout_geometry.py'),
   layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','6','--require-native-table-slide','9'],
   explicitTotalSlideCount:data.length,requiredNativeChartOwnerSlides:[5,7,10],requiredNativeTableOwnerSlides:[6,9],
   materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Aptos','Georgia']},verifyArtifactToolImport:true,
   receiptPath:path.join(build,`validation-${Date.now()}.json`)});
}else await fs.copyFile(path.join(build,'candidate.pptx'),path.join(root,'presentation/Final_Pitch.pptx'));
try {
 const pdf=await p.export({format:'pdf'});await fs.writeFile(path.join(root,'presentation/Final_Pitch.pdf'),new Uint8Array(await pdf.arrayBuffer()));
}catch(error){
 console.warn('Native PDF exporter unavailable; using slide-render PDF:',error.message);
 const result=spawnSync(process.env.AEGIS_RUNTIME_PYTHON||'python',[path.join(root,'scripts/render_pitch_pdf.py'),build],{encoding:'utf8'});
 if(result.status!==0)throw new Error(result.stderr);console.log(result.stdout.trim());
}
console.log('Exported',data.length,'slides to',root);
} catch(error) { console.error(error.message); process.exitCode=1; }
