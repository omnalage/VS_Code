let movedCount = 0; // how many images have been dragged from their original spot (counted once per image)

document.addEventListener("dragon-dragged-right", () => {
  movedCount++;
  const status = document.getElementById("status");
  if (status) status.textContent = `Moved: ${movedCount}/2`;
  if (movedCount === 2) { // since we have 2 dragons
    document.getElementById("title").textContent = "two moves are done";
  }
});

function enableDragonDrag(dragon) {
  let originX = null;
  let originY = null;
  let offsetX = 0;
  let offsetY = 0;
  let dragStarted = false;
  let completionReported = false; // ensure each image only increments once

  let vph = window.innerHeight - 200;
  let vpw = window.innerWidth - 200;

  function onDragStart(event) {
    event.preventDefault();
    originX = event.clientX;
    originY = event.clientY;
    dragStarted = true;
    dragon.setPointerCapture(event.pointerId);
  }

  function onDragMove(event) {
    if (!dragStarted) return;
    event.preventDefault();

    const deltaX = event.clientX - originX;
    const deltaY = event.clientY - originY;

    let translateX = offsetX + deltaX;
    let translateY = offsetY + deltaY;

    // boundaries
    if (translateX < 0) translateX = 0;
    if (translateY < 0) translateY = 0;
    if (translateX > vpw) translateX = vpw;
    if (translateY > vph) translateY = vph;

    dragon.style.transform = `translate(${translateX}px, ${translateY}px)`;
  }

  function onDragEnd(event) {
    dragStarted = false;
    offsetX += event.clientX - originX;
    offsetY += event.clientY - originY;

    // Preserve original behavior: count any horizontal move from origin
    if (!completionReported && offsetX !== 0) {
      completionReported = true;
      document.dispatchEvent(new CustomEvent("dragon-dragged-right"));
    }
  }

  dragon.addEventListener('pointerdown', onDragStart);
  dragon.addEventListener('pointerup', onDragEnd);
  dragon.addEventListener('pointermove', onDragMove);
}

// Apply to all dragons
document.querySelectorAll('img').forEach(enableDragonDrag);
