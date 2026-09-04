export default function Button({children,variant='primary',className='',...props}){return <button className={`kids-btn ${variant} ${className}`} {...props}>{children}</button>}
