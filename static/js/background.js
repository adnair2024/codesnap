let scene, camera, renderer, mesh;

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('bg-canvas'), antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    const geometry = new THREE.PlaneGeometry(20, 20, 50, 50);
    const material = new THREE.MeshPhongMaterial({
        color: 0x1a1a1a,
        wireframe: false,
        side: THREE.DoubleSide,
        flatShading: true
    });

    mesh = new THREE.Mesh(geometry, material);
    mesh.rotation.x = -Math.PI / 3;
    scene.add(mesh);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(0, 1, 1).normalize();
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0x404040); // soft white light
    scene.add(ambientLight);

    // Update colors based on system theme
    updateTheme();
}

function updateTheme() {
    const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (isDarkMode) {
        mesh.material.color.setHex(0x0a0a0a);
        scene.background = new THREE.Color(0x0a0a0a);
    } else {
        mesh.material.color.setHex(0xf0f0f0);
        scene.background = new THREE.Color(0xf0f0f0);
    }
}

let mouseX = 0;
let mouseY = 0;

window.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth) - 0.5;
    mouseY = (e.clientY / window.innerHeight) - 0.5;
});

function animate() {
    requestAnimationFrame(animate);

    const time = Date.now() * 0.001;
    const positions = mesh.geometry.attributes.position.array;

    for (let i = 0; i < positions.length; i += 3) {
        const x = positions[i];
        const y = positions[i + 1];
        positions[i + 2] = Math.sin(x * 0.5 + time) * 0.5 + Math.cos(y * 0.5 + time) * 0.5;
    }
    mesh.geometry.attributes.position.needsUpdate = true;

    mesh.rotation.z += 0.001;
    mesh.position.x += (mouseX - mesh.position.x) * 0.05;
    mesh.position.y += (-mouseY - mesh.position.y) * 0.05;

    renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateTheme);

init();
animate();
