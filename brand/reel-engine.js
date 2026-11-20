/* Reel animation engine. Page defines:
     <div class="scene" id="s1"> ... </div> ...   and   window.SC = [["s1", seconds], ...]
   Inside a scene:
     .bg            -> slow Ken Burns zoom
     .a             -> animated element; data-in="seconds after scene start"
                       data-from="up|down|left" (default left) ; class "pop" = scale-in with overshoot
   tools/render_reel.py calls show(i, t, dur) for every frame (deterministic, no CSS animations). */
(function(){
  const ease=t=>1-Math.pow(1-Math.max(0,Math.min(1,t)),3);
  const back=t=>{t=Math.max(0,Math.min(1,t));const c=1.7;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2)};
  window.show=function(i,t,dur){
    const SC=window.SC;
    document.querySelectorAll('.scene').forEach(s=>s.style.display='none');
    const s=document.getElementById(SC[i][0]); s.style.display='block';
    const bg=s.querySelector('.bg'); if(bg){bg.style.transform=`scale(${1+0.08*(t/dur)}) translateY(${-14*t/dur}px)`;}
    s.querySelectorAll('.a').forEach(el=>{
      const st=parseFloat(el.dataset.in||0), p=(t-st)/0.45, e=ease(p), from=el.dataset.from;
      let tr;
      if(el.classList.contains('pop')) tr=`scale(${0.6+0.4*back(p)})`;
      else if(from==='up') tr=`translateY(${(1-e)*160}px)`;
      else if(from==='down') tr=`translateY(${-(1-e)*120}px)`;
      else tr=`translateX(${(1-e)*-90}px)`;
      el.style.opacity=Math.min(1,Math.max(0,p*1.6)); el.style.transform=tr;
    });
    s.style.opacity=(i<SC.length-1 && t>dur-0.12)?(dur-t)/0.12:1;
  };
})();
