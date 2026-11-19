// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
export function scheduleIconLibrary(window,document,render){
  if(window.lucide){render();return;}
  function load(){
    const script=document.createElement("script");
    script.src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js";
    script.integrity="sha256-NBFpKCDLjUdUP2lJaqJf1gOjWPRJgEb0HFCKWjNCIQ4=";
    script.crossOrigin="anonymous";
    script.async=true;
    script.addEventListener("load",render,{once:true});
    document.head.append(script);
  }
  // Optional icon delivery must not hold either application or its load event.
  if(document.readyState==="complete")load();
  else window.addEventListener("load",load,{once:true});
}
