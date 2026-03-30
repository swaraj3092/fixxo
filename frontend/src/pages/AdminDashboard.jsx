import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const C = {
  bg:'#04060f', surface:'#0a0d1a', card:'#0d1121',
  border:'rgba(0,212,255,0.12)', borderHov:'rgba(0,212,255,0.35)',
  cyan:'#00d4ff', cyanDim:'rgba(0,212,255,0.12)',
  amber:'#f59e0b', green:'#10b981', red:'#ef4444', purple:'#a855f7',
  textPrimary:'#e2e8f0', textMuted:'#4a5568', textSub:'#94a3b8',
};

const GLOBAL_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:${C.bg};font-family:'DM Sans',sans-serif;color:${C.textPrimary};}
  ::-webkit-scrollbar{width:4px;}
  ::-webkit-scrollbar-track{background:${C.bg};}
  ::-webkit-scrollbar-thumb{background:${C.cyanDim};border-radius:4px;}
  @keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
  @keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.7)}}
  @keyframes scanline{0%{transform:translateY(-100%)}100%{transform:translateY(100vh)}}
  @keyframes spin{to{transform:rotate(360deg)}}
  .stat-card{
    background:${C.card};border:1px solid ${C.border};border-radius:14px;
    padding:20px 22px;transition:border-color .25s,box-shadow .25s,transform .2s;
    animation:fadeUp .4s ease both;
  }
  .stat-card:hover{border-color:rgba(0,212,255,.3);box-shadow:0 0 20px rgba(0,212,255,.07);transform:translateY(-2px);}
  .c-card{
    background:${C.card};border:1px solid ${C.border};border-radius:12px;
    margin-bottom:8px;transition:border-color .2s,box-shadow .2s;
    animation:fadeUp .35s ease both;overflow:hidden;
  }
  .c-card:hover{border-color:rgba(0,212,255,.25);box-shadow:0 4px 24px rgba(0,0,0,.3);}
  .tab-btn{
    padding:11px 20px;background:none;border:none;cursor:pointer;
    font-family:'DM Sans',sans-serif;font-weight:600;font-size:13px;
    color:${C.textMuted};border-bottom:2px solid transparent;transition:all .2s;white-space:nowrap;
  }
  .tab-btn:hover{color:${C.textSub};}
  .tab-btn.active{color:${C.cyan};border-bottom-color:${C.cyan};}
  .chip{
    padding:6px 13px;border-radius:20px;border:1px solid rgba(255,255,255,.08);
    background:transparent;color:${C.textMuted};font-size:12px;font-weight:600;
    cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif;
  }
  .chip:hover{background:rgba(255,255,255,.06);color:${C.textSub};}
  .chip.active{background:rgba(0,212,255,.12);color:${C.cyan};border-color:rgba(0,212,255,.3);}
  .live-dot{width:7px;height:7px;border-radius:50%;background:${C.green};display:inline-block;animation:pulse-dot 1.8s ease-in-out infinite;}
  .expand-anim{animation:fadeUp .2s ease both;}
`;

const PRIORITY_COL = { URGENT:'#ef4444', HIGH:'#f97316', MEDIUM:'#f59e0b', LOW:'#3b82f6' };
const STATUS_MAP = {
  PENDING:      { bg:'rgba(245,158,11,.12)',  color:'#f59e0b', label:'⏳ Pending' },
  IN_PROGRESS:  { bg:'rgba(59,130,246,.12)',  color:'#60a5fa', label:'🔧 In Progress' },
  RESOLVED:     { bg:'rgba(16,185,129,.12)',  color:'#10b981', label:'✅ Resolved' },
  CANT_RESOLVE: { bg:'rgba(239,68,68,.12)',   color:'#ef4444', label:"❌ Can't Resolve" },
};
const CAT_ICONS = { PLUMBING:'🚰',ELECTRICAL:'⚡',WIFI:'📶',CLEANLINESS:'🧹',SECURITY:'🔒',FOOD:'🍽️',FURNITURE:'🪑',OTHER:'📋' };

function Stars({ rating, size=15 }) {
  return (
    <span>
      {[1,2,3,4,5].map(s => (
        <span key={s} style={{ color: s<=rating ? C.amber : 'rgba(255,255,255,.12)', fontSize:size }}>★</span>
      ))}
    </span>
  );
}

function LiveClock() {
  const [t, setT] = useState(new Date());
  useEffect(() => { const i = setInterval(()=>setT(new Date()),1000); return ()=>clearInterval(i); },[]);
  return <span style={{ fontFamily:'JetBrains Mono', fontSize:12, color:C.textMuted }}>{t.toLocaleTimeString()}</span>;
}

function InfoCell({ label, value, color }) {
  return (
    <div>
      <div style={{ color:C.textMuted, fontSize:10, textTransform:'uppercase', letterSpacing:'.08em', marginBottom:3 }}>{label}</div>
      <div style={{ color:color||C.textPrimary, fontSize:13, fontWeight:600 }}>{value||'N/A'}</div>
    </div>
  );
}

function ComplaintCard({ complaint, feedback }) {
  const [open, setOpen] = useState(false);
  const [imgError, setImgError] = useState(false);
  const st = STATUS_MAP[complaint.status] || STATUS_MAP.PENDING;
  const proxyUrl = complaint.media_url
    ? `${API_URL}/api/proxy-image?url=${encodeURIComponent(complaint.media_url)}`
    : null;

  return (
    <div className="c-card">
      <div onClick={()=>setOpen(!open)} style={{ display:'flex', alignItems:'center', padding:'13px 16px', cursor:'pointer', gap:10 }}>
        <div style={{ width:8, height:8, borderRadius:'50%', flexShrink:0, background:PRIORITY_COL[complaint.priority]||C.amber, boxShadow:`0 0 6px ${PRIORITY_COL[complaint.priority]||C.amber}66` }} />
        <span style={{ fontFamily:'JetBrains Mono', fontSize:11, color:C.cyan, minWidth:68, flexShrink:0 }}>
          #{complaint.resolve_token?.slice(0,8)}
        </span>
        <span style={{ flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', fontSize:13 }}>
          <span style={{ color:C.textPrimary, fontWeight:600 }}>{CAT_ICONS[complaint.category]} {complaint.category}</span>
          <span style={{ color:C.textMuted, marginLeft:8 }}>{complaint.student_name} · {complaint.hostel_name} #{complaint.room_number}</span>
        </span>
        <div style={{ display:'flex', gap:5, alignItems:'center', flexShrink:0 }}>
          <span style={{ background:st.bg, color:st.color, padding:'3px 9px', borderRadius:20, fontSize:11, fontWeight:700 }}>{st.label}</span>
          {proxyUrl && !imgError && <span style={{ background:'rgba(168,85,247,.15)', color:'#d8b4fe', padding:'3px 7px', borderRadius:20, fontSize:11 }}>📷</span>}
          {feedback && <span style={{ background:'rgba(245,158,11,.12)', color:C.amber, padding:'3px 7px', borderRadius:20, fontSize:11, fontFamily:'JetBrains Mono' }}>★{feedback.rating}</span>}
          <span style={{ color:C.textMuted, fontSize:13, marginLeft:2 }}>{open?'▲':'▼'}</span>
        </div>
      </div>

      {open && (
        <div className="expand-anim" style={{ borderTop:`1px solid ${C.border}`, padding:'16px 20px', background:'rgba(0,0,0,.25)' }}>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(140px,1fr))', gap:12, marginBottom:14 }}>
            <InfoCell label="Student" value={complaint.student_name} />
            <InfoCell label="Phone" value={complaint.student_phone} />
            <InfoCell label="Location" value={`${complaint.hostel_name}, Rm ${complaint.room_number}`} />
            <InfoCell label="Priority" value={complaint.priority} color={PRIORITY_COL[complaint.priority]} />
            <InfoCell label="Category" value={complaint.category} />
            <InfoCell label="Time" value={new Date(complaint.created_at).toLocaleString()} />
          </div>

          <div style={{ background:'rgba(0,212,255,.05)', border:'1px solid rgba(0,212,255,.12)', borderRadius:8, padding:'10px 14px', marginBottom:12 }}>
            <div style={{ color:C.cyan, fontSize:10, textTransform:'uppercase', letterSpacing:'.08em', marginBottom:5 }}>💬 Complaint</div>
            <div style={{ color:C.textSub, fontSize:13, lineHeight:1.6 }}>{complaint.raw_message}</div>
          </div>

          {complaint.cant_resolve_reason && (
            <div style={{ background:'rgba(239,68,68,.06)', border:'1px solid rgba(239,68,68,.2)', borderRadius:8, padding:'10px 14px', marginBottom:12 }}>
              <div style={{ color:'#fca5a5', fontSize:10, textTransform:'uppercase', letterSpacing:'.08em', marginBottom:5 }}>⚠️ Can't Resolve Reason</div>
              <div style={{ color:C.textSub, fontSize:13 }}>{complaint.cant_resolve_reason}</div>
            </div>
          )}

          {proxyUrl && !imgError && (
            <div style={{ marginBottom:12 }}>
              <div style={{ color:C.purple, fontSize:10, textTransform:'uppercase', letterSpacing:'.08em', marginBottom:8 }}>📷 Attached Photo</div>
              <img
                src={proxyUrl}
                alt="Complaint photo"
                onError={()=>setImgError(true)}
                style={{ maxWidth:'100%', maxHeight:280, borderRadius:10, border:'1px solid rgba(168,85,247,.25)', display:'block' }}
              />
            </div>
          )}

          {feedback && (
            <div style={{ background:'rgba(16,185,129,.06)', border:'1px solid rgba(16,185,129,.2)', borderRadius:8, padding:'12px 14px' }}>
              <div style={{ color:C.green, fontSize:10, textTransform:'uppercase', letterSpacing:'.08em', marginBottom:8 }}>⭐ Student Feedback</div>
              <div style={{ display:'flex', alignItems:'center', gap:10, flexWrap:'wrap' }}>
                <Stars rating={feedback.rating} size={17} />
                <span style={{ color:C.textMuted, fontSize:12 }}>{['','Very Poor 😞','Poor 😕','OK 😐','Good 😊','Excellent! 🎉'][feedback.rating]}</span>
              </div>
              {feedback.feedback_text && (
                <div style={{ color:C.textSub, fontSize:13, marginTop:8, fontStyle:'italic', lineHeight:1.6 }}>"{feedback.feedback_text}"</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  const [tab, setTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [searchQ, setSearchQ] = useState('');
  const navigate = useNavigate();

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      const [sR, stR, cR] = await Promise.all([
        axios.get(`${API_URL}/api/admin/stats`,      { withCredentials:true }),
        axios.get(`${API_URL}/api/admin/students`,   { withCredentials:true }),
        axios.get(`${API_URL}/api/admin/complaints`, { withCredentials:true }),
      ]);
      setStats(sR.data); setStudents(stR.data); setComplaints(cR.data);
      const resolved = cR.data.filter(c=>c.status==='RESOLVED');
      const fbRes = await Promise.all(
        resolved.map(c =>
          axios.get(`${API_URL}/api/feedback/${c.resolve_token}`,{withCredentials:true})
            .then(r => r.data ? {...r.data, resolve_token:c.resolve_token} : null)
            .catch(()=>null)
        )
      );
      setFeedbacks(fbRes.filter(Boolean));
    } catch(e) { if(e.response?.status===401) navigate('/admin/login'); }
    finally { setLoading(false); }
  }, [navigate]);

  useEffect(()=>{
    if(!localStorage.getItem('admin')){ navigate('/admin/login'); return; }
    fetchAll();
  },[fetchAll, navigate]);

  const handleLogout = async () => {
    try{ await axios.post(`${API_URL}/api/admin/logout`,{},{withCredentials:true}); }catch{}
    localStorage.removeItem('admin'); navigate('/admin/login');
  };

  const getFB = token => feedbacks.find(f=>f.resolve_token===token);
  const avgRating = feedbacks.length
    ? (feedbacks.reduce((s,f)=>s+f.rating,0)/feedbacks.length).toFixed(1) : null;

  const filtered = complaints
    .filter(c => filter==='ALL'||c.status===filter)
    .filter(c => !searchQ||[c.student_name,c.category,c.hostel_name,c.resolve_token]
      .some(v=>v?.toLowerCase().includes(searchQ.toLowerCase())));

  if(loading) return (
    <>
      <style>{GLOBAL_CSS}</style>
      <div style={{minHeight:'100vh',background:C.bg,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',gap:16}}>
        <div style={{width:40,height:40,border:`3px solid ${C.cyanDim}`,borderTopColor:C.cyan,borderRadius:'50%',animation:'spin .8s linear infinite'}}/>
        <div style={{fontFamily:'JetBrains Mono',color:C.textMuted,fontSize:13}}>INITIALIZING DASHBOARD...</div>
      </div>
    </>
  );

  const TABS = [
    {id:'overview', label:'Overview'},
    {id:'complaints', label:`Complaints (${complaints.length})`},
    {id:'feedback', label:`Feedback${feedbacks.length?` ★${avgRating}`:''}`},
    {id:'students', label:`Students (${students.length})`},
  ];

  const STATS = [
    {icon:'🎫',label:'Total',      value:complaints.length,                                    color:C.cyan},
    {icon:'⏳',label:'Pending',    value:complaints.filter(c=>c.status==='PENDING').length,     color:C.amber},
    {icon:'🔧',label:'In Progress',value:complaints.filter(c=>c.status==='IN_PROGRESS').length, color:'#60a5fa'},
    {icon:'✅',label:'Resolved',   value:complaints.filter(c=>c.status==='RESOLVED').length,   color:C.green},
    {icon:'❌',label:"Can't Resolve",value:complaints.filter(c=>c.status==='CANT_RESOLVE').length,color:C.red},
    {icon:'⭐',label:'Avg Rating', value:avgRating?`${avgRating}/5`:'—',                       color:C.amber},
    {icon:'💬',label:'Feedbacks',  value:feedbacks.length,                                     color:C.purple},
    {icon:'👥',label:'Students',   value:students.length,                                      color:'#34d399'},
  ];

  return (
    <>
      <style>{GLOBAL_CSS}</style>

      {/* Scanline overlay */}
      <div style={{position:'fixed',inset:0,pointerEvents:'none',zIndex:0,overflow:'hidden',opacity:.015}}>
        <div style={{position:'absolute',left:0,right:0,height:2,background:`linear-gradient(transparent,${C.cyan},transparent)`,animation:'scanline 8s linear infinite'}}/>
      </div>

      <div style={{position:'relative',zIndex:1,minHeight:'100vh'}}>

        {/* Header */}
        <header style={{background:'rgba(4,6,15,.92)',backdropFilter:'blur(16px)',borderBottom:`1px solid ${C.border}`,position:'sticky',top:0,zIndex:100}}>
          <div style={{maxWidth:1280,margin:'0 auto',padding:'0 24px',display:'flex',alignItems:'center',justifyContent:'space-between',height:56}}>
            <div style={{display:'flex',alignItems:'center',gap:14}}>
              <span style={{fontFamily:'Syne',fontWeight:800,fontSize:20,color:C.cyan,letterSpacing:'-.02em'}}>FIXXO</span>
              <span style={{color:C.textMuted,fontSize:18}}>|</span>
              <span style={{fontFamily:'JetBrains Mono',fontSize:12,color:C.textMuted}}>ADMIN CONSOLE</span>
              <span style={{display:'flex',alignItems:'center',gap:5,background:'rgba(16,185,129,.1)',border:'1px solid rgba(16,185,129,.25)',padding:'3px 9px',borderRadius:20}}>
                <span className="live-dot"/>
                <span style={{fontFamily:'JetBrains Mono',fontSize:10,color:C.green}}>LIVE</span>
              </span>
            </div>
            <div style={{display:'flex',alignItems:'center',gap:14}}>
              <LiveClock/>
              <button onClick={fetchAll} style={{background:'transparent',border:`1px solid ${C.border}`,color:C.textMuted,padding:'6px 12px',borderRadius:8,cursor:'pointer',fontSize:12,fontFamily:'DM Sans'}}>↺</button>
              <button onClick={handleLogout} style={{background:'rgba(239,68,68,.1)',border:'1px solid rgba(239,68,68,.25)',color:'#fca5a5',padding:'6px 14px',borderRadius:8,cursor:'pointer',fontSize:12,fontFamily:'DM Sans',fontWeight:600}}>Logout</button>
            </div>
          </div>
        </header>

        {/* Tabs */}
        <div style={{background:'rgba(4,6,15,.7)',borderBottom:`1px solid ${C.border}`}}>
          <div style={{maxWidth:1280,margin:'0 auto',padding:'0 24px',display:'flex',overflowX:'auto'}}>
            {TABS.map(t=>(
              <button key={t.id} className={`tab-btn${tab===t.id?' active':''}`} onClick={()=>setTab(t.id)}>{t.label}</button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div style={{maxWidth:1280,margin:'0 auto',padding:'28px 24px'}}>

          {/* OVERVIEW */}
          {tab==='overview' && (
            <div>
              <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(148px,1fr))',gap:10,marginBottom:28}}>
                {STATS.map((s,i)=>(
                  <div className="stat-card" key={s.label} style={{animationDelay:`${i*.05}s`}}>
                    <div style={{fontSize:22,marginBottom:8}}>{s.icon}</div>
                    <div style={{fontFamily:'JetBrains Mono',fontSize:28,fontWeight:700,color:s.color,lineHeight:1}}>{s.value}</div>
                    <div style={{color:C.textMuted,fontSize:11,textTransform:'uppercase',letterSpacing:'.08em',marginTop:6}}>{s.label}</div>
                  </div>
                ))}
              </div>
              <div style={{background:C.card,border:`1px solid ${C.border}`,borderRadius:14,padding:'20px 20px 12px'}}>
                <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:16}}>
                  <span style={{fontFamily:'Syne',fontSize:16,fontWeight:700}}>Recent Complaints</span>
                  <button onClick={()=>setTab('complaints')} style={{background:'transparent',border:'none',color:C.cyan,fontSize:12,cursor:'pointer',fontFamily:'DM Sans'}}>View all →</button>
                </div>
                {complaints.slice(0,6).map(c=><ComplaintCard key={c.id} complaint={c} feedback={getFB(c.resolve_token)}/>)}
              </div>
            </div>
          )}

          {/* COMPLAINTS */}
          {tab==='complaints' && (
            <div>
              <div style={{display:'flex',gap:8,marginBottom:16,flexWrap:'wrap',alignItems:'center'}}>
                {['ALL','PENDING','IN_PROGRESS','RESOLVED','CANT_RESOLVE'].map(s=>(
                  <button key={s} className={`chip${filter===s?' active':''}`} onClick={()=>setFilter(s)}>
                    {s==='ALL'?`All · ${complaints.length}`:`${STATUS_MAP[s]?.label} · ${complaints.filter(c=>c.status===s).length}`}
                  </button>
                ))}
                <input
                  value={searchQ} onChange={e=>setSearchQ(e.target.value)}
                  placeholder="Search…"
                  style={{marginLeft:'auto',background:'rgba(255,255,255,.04)',border:`1px solid ${C.border}`,borderRadius:8,padding:'7px 14px',color:C.textPrimary,fontSize:13,fontFamily:'DM Sans',outline:'none',minWidth:200}}
                />
              </div>
              {filtered.length===0
                ? <div style={{textAlign:'center',color:C.textMuted,padding:60}}>No complaints match your filter.</div>
                : filtered.map(c=><ComplaintCard key={c.id} complaint={c} feedback={getFB(c.resolve_token)}/>)
              }
            </div>
          )}

          {/* FEEDBACK */}
          {tab==='feedback' && (
            <div>
              <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(170px,1fr))',gap:10,marginBottom:24}}>
                <div className="stat-card">
                  <div style={{fontFamily:'JetBrains Mono',fontSize:36,fontWeight:700,color:C.amber}}>{avgRating||'—'}</div>
                  <div style={{marginTop:6}}><Stars rating={Math.round(avgRating)||0} size={15}/></div>
                  <div style={{color:C.textMuted,fontSize:11,textTransform:'uppercase',letterSpacing:'.08em',marginTop:8}}>Avg Rating</div>
                </div>
                <div className="stat-card">
                  <div style={{fontFamily:'JetBrains Mono',fontSize:36,fontWeight:700,color:C.green}}>{feedbacks.length}</div>
                  <div style={{color:C.textMuted,fontSize:11,textTransform:'uppercase',letterSpacing:'.08em',marginTop:10}}>Total Feedbacks</div>
                </div>
                <div className="stat-card" style={{gridColumn:'span 2'}}>
                  <div style={{color:C.textMuted,fontSize:11,textTransform:'uppercase',letterSpacing:'.08em',marginBottom:12}}>Rating Breakdown</div>
                  {[5,4,3,2,1].map(star=>{
                    const count=feedbacks.filter(f=>f.rating===star).length;
                    const pct=feedbacks.length?Math.round(count/feedbacks.length*100):0;
                    return (
                      <div key={star} style={{display:'flex',alignItems:'center',gap:8,marginBottom:7}}>
                        <span style={{color:C.amber,fontFamily:'JetBrains Mono',fontSize:11,width:10}}>{star}</span>
                        <span style={{color:C.amber,fontSize:12}}>★</span>
                        <div style={{flex:1,background:'rgba(255,255,255,.06)',borderRadius:4,height:7,overflow:'hidden'}}>
                          <div style={{width:`${pct}%`,height:'100%',background:`linear-gradient(90deg,${C.amber},#fcd34d)`,borderRadius:4,transition:'width .6s ease'}}/>
                        </div>
                        <span style={{color:C.textMuted,fontFamily:'JetBrains Mono',fontSize:11,width:20,textAlign:'right'}}>{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {feedbacks.length===0
                ? (
                  <div style={{textAlign:'center',color:C.textMuted,padding:60,background:C.card,border:`1px solid ${C.border}`,borderRadius:14}}>
                    <div style={{fontSize:48,marginBottom:12}}>⭐</div>
                    <div>No feedbacks yet.</div>
                    <div style={{fontSize:12,marginTop:4}}>Feedbacks appear once students rate resolved complaints.</div>
                  </div>
                )
                : feedbacks.map(fb=>{
                    const c=complaints.find(c=>c.resolve_token===fb.resolve_token);
                    return (
                      <div key={fb.id||fb.resolve_token} className="c-card" style={{padding:'16px 20px'}}>
                        <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',flexWrap:'wrap',gap:12}}>
                          <div>
                            <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:6}}>
                              <Stars rating={fb.rating} size={18}/>
                              <span style={{color:C.textMuted,fontSize:12}}>{['','Very Poor','Poor','OK','Good','Excellent!'][fb.rating]}</span>
                            </div>
                            {fb.feedback_text&&<div style={{color:C.textSub,fontSize:13,fontStyle:'italic',marginBottom:8,lineHeight:1.6}}>"{fb.feedback_text}"</div>}
                            {c&&<div style={{color:C.textMuted,fontSize:12}}>{CAT_ICONS[c.category]} {c.category} · {c.hostel_name} Rm {c.room_number} · {c.student_name}</div>}
                          </div>
                          <span style={{fontFamily:'JetBrains Mono',fontSize:11,color:C.cyan,background:C.cyanDim,padding:'4px 10px',borderRadius:20,flexShrink:0}}>
                            #{fb.resolve_token?.slice(0,8)}
                          </span>
                        </div>
                      </div>
                    );
                  })
              }
            </div>
          )}

          {/* STUDENTS */}
          {tab==='students' && (
            <div style={{background:C.card,border:`1px solid ${C.border}`,borderRadius:14,padding:'20px 20px 8px',overflowX:'auto'}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:18}}>
                <span style={{fontFamily:'Syne',fontSize:16,fontWeight:700}}>Registered Students</span>
                <span style={{fontFamily:'JetBrains Mono',color:C.cyan,fontSize:13}}>{students.length} total</span>
              </div>
              <table style={{width:'100%',borderCollapse:'collapse'}}>
                <thead>
                  <tr style={{borderBottom:`1px solid ${C.border}`}}>
                    {['Name','Roll No','Hostel','Room','WhatsApp','Registered'].map(h=>(
                      <th key={h} style={{textAlign:'left',padding:'8px 12px',color:C.textMuted,fontSize:11,textTransform:'uppercase',letterSpacing:'.07em',fontWeight:600}}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {students.map((s,i)=>(
                    <tr key={s.id} style={{borderBottom:'1px solid rgba(255,255,255,.04)',animation:`fadeUp .3s ease ${i*.03}s both`}}>
                      <td style={{padding:'11px 12px',color:C.textPrimary,fontWeight:600,fontSize:13}}>{s.student_name}</td>
                      <td style={{padding:'11px 12px',fontFamily:'JetBrains Mono',color:C.cyan,fontSize:12}}>{s.roll_number}</td>
                      <td style={{padding:'11px 12px',color:C.textSub,fontSize:13}}>{s.hostel_name}</td>
                      <td style={{padding:'11px 12px',color:C.textSub,fontSize:13}}>{s.room_number}</td>
                      <td style={{padding:'11px 12px',fontFamily:'JetBrains Mono',color:C.textMuted,fontSize:12}}>{s.phone_number}</td>
                      <td style={{padding:'11px 12px',color:C.textMuted,fontSize:12}}>{s.created_at?new Date(s.created_at).toLocaleDateString():'—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {students.length===0&&<div style={{textAlign:'center',color:C.textMuted,padding:48}}>No students registered yet.</div>}
            </div>
          )}
        </div>
      </div>
    </>
  );
}