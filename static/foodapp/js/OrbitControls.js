// OrbitControls minimal stub
console.log("OrbitControls loaded");
if (window.THREE) {
  window.THREE.OrbitControls = function() {
    return {
      enableDamping: true,
      dampingFactor: 0.05,
      enableZoom: true,
      update: function() {}
    };
  };
} 