const batches = {
    widgetA: [
      "Exploded on first use. Sparks everywhere.",
      "Caught fire and burned my countertop.",
      "Burned my hand badly while operating.",
      "Tripped the breaker and filled the room with smoke."
    ],
    widgetB: [
      "Works great, no complaints!",
      "Really fast and reliable device.",
      "Started smoking after a week.",
      "Dangerous wiring — avoid."
    ]
  };
  
  async function sendBatch(name){
    const pid = name.toLowerCase();
    for (const txt of batches[name]){
      await fetch('/submit_review', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({product_id:pid,text:txt})
      });
    }
    alert('Batch sent ✔︎');
  }
  