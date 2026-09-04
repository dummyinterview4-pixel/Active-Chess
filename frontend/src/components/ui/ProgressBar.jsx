export default function ProgressBar({value=0}){return <div className="kids-progress"><div style={{width:`${Math.max(0,Math.min(100,value))}%`}}/></div>}
