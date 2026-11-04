const api = (path, options={}) => fetch(window.API_BASE_URL + path, {
  ...options, headers: {"Content-Type":"application/json", ...(options.headers||{})}
});
const msg = (text, error=false) => { const el=document.getElementById("message"); if(el){el.textContent=text;el.style.color=error?"#b42318":"#167044";} };
const reg = document.getElementById("registerForm");
if(reg) reg.addEventListener("submit", async e => {
  e.preventDefault(); const f=new FormData(reg); const data=Object.fromEntries(f.entries());
  data.full_name=data.full_name.trim().replace(/\s+/g," ").replace(/\b\w/g,c=>c.toUpperCase());
  data.subjects=data.subjects.split(",").map(x=>x.trim()).filter(Boolean);
  data.levels=data.levels.split(",").map(x=>x.trim()).filter(Boolean);
  if(!data.whatsapp) data.whatsapp=null;
  try { const r=await api("/api/auth/register",{method:"POST",body:JSON.stringify(data)}); const j=await r.json(); if(!r.ok) throw Error(j.detail||"Registration failed"); msg(j.message); reg.reset(); }
  catch(err){msg(err.message+" — Check that the API server is running.",true);}
});
const login=document.getElementById("loginForm");
if(login) login.addEventListener("submit",async e=>{
  e.preventDefault(); const data=Object.fromEntries(new FormData(login).entries());
  try {const r=await api("/api/auth/login",{method:"POST",body:JSON.stringify(data)});const j=await r.json();if(!r.ok)throw Error(j.detail||"Login failed");sessionStorage.setItem("dav_token",j.access_token);msg("Login successful. Welcome, "+j.teacher.name+".");}
  catch(err){msg(err.message,true);}
});
