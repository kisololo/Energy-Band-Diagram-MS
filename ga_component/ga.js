// ga.js — runs in Streamlit’s top-level JS sandbox (NOT in the iframe)

const script1 = document.createElement("script");
script1.async = true;
script1.src = "https://www.googletagmanager.com/gtag/js?id=G-7SJTF762GX";
document.head.appendChild(script1);

const script2 = document.createElement("script");
script2.innerHTML = `
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-7SJTF762GX');
`;
document.head.appendChild(script2);

// Notify Streamlit that the script has been loaded
window.parent.postMessage({ type: "GA4_LOADED" }, "*");
