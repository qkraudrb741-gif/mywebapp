import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title="Streamlit Sudden Attack 3D",
    page_icon="🎯",
    layout="wide"
)

# 세션 상태 초기화 (화면 전환 관리)
if "page" not in st.session_state:
    st.session_state.page = "main"

# -----------------------------------------------------------------------------
# 1. 메인 메뉴 화면
# -----------------------------------------------------------------------------
if st.session_state.page == "main":
    st.title("🎯 Streamlit Sudden Attack")
    st.caption("Streamlit 기반의 웹 1인칭 슈팅(FPS) 게임")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("메인 메뉴")
        if st.button("🎮 게임 시작", use_container_width=True, type="primary"):
            st.session_state.page = "game"
            st.rerun()

        if st.button("📖 게임 방법", use_container_width=True):
            st.session_state.page = "howto"
            st.rerun()

# -----------------------------------------------------------------------------
# 2. 게임 방법 화면
# -----------------------------------------------------------------------------
elif st.session_state.page == "howto":
    st.title("📖 게임 방법")
    st.divider()

    st.markdown("""
    ### 🎮 조작법
    * **마우스 클릭**: 게임 화면을 클릭하면 **마우스 포인터가 가려지며(Pointer Lock)** 1인칭 시점으로 전환됩니다.
    * **마우스 이동**: 시화 회전 (상, 하, 좌, 우 Look)
    * **마우스 좌클릭**: 사격 (총을 쏩니다)
    * **W / A / S / D**: 이동 (전진 / 좌측 / 후진 / 우측)
    * **ESC 키**: 마우스 포인터 잠금 해제

    ### 🎯 게임 규칙
    1. 게임이 시작되면 무작위 위치에 **적(적색 3D 표적)**이 등장합니다.
    2. 적은 일정 주기마다 플레이어를 공격하며, 플레이어의 **HP가 0이 되면 게임 오버**가 됩니다.
    3. 적의 머리를 맞추면 **헤드샷 추가 대미지**가 적용됩니다.
    4. 적을 처치하면 즉시 새로운 적이 등장하며 점수가 상승합니다.
    """)

    if st.button("⬅️ 메인 메뉴로 돌아가기", type="secondary"):
        st.session_state.page = "main"
        st.rerun()

# -----------------------------------------------------------------------------
# 3. 게임 플레이 화면 (Three.js 기반 3D Engine)
# -----------------------------------------------------------------------------
elif st.session_state.page == "game":
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader("🎯 사격장 (FPS Battle Zone)")
    with col2:
        if st.button("🚪 메인 메뉴로 나가기", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()

    # Three.js 기반 3D Canvas 게임 엔진 HTML/JS
    game_html = 
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #000; user-select: none; }
            #game-container { width: 100vw; height: 100vh; position: relative; }
            
            /* UI 래퍼 */
            #ui-layer {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                pointer-events: none; display: flex; flex-direction: column; justify-content: space-between;
                padding: 20px; box-sizing: border-box;
            }
            .hud { color: #00ffcc; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 4px #000; }
            #crosshair {
                position: absolute; top: 50%; left: 50%; width: 12px; height: 12px;
                margin-top: -6px; margin-left: -6px; pointer-events: none;
            }
            #crosshair::before, #crosshair::after {
                content: ''; position: absolute; background: #00ffcc;
            }
            #crosshair::before { top: 5px; left: 0; width: 12px; height: 2px; }
            #crosshair::after { top: 0; left: 5px; width: 2px; height: 12px; }

            /* 안내 플레이스홀더 */
            #blocker {
                position: absolute; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7);
                display: flex; flex-direction: column; justify-content: center; align-items: center;
                color: white; cursor: pointer; pointer-events: auto;
            }
            #damage-overlay {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(255, 0, 0, 0.3); opacity: 0; transition: opacity 0.1s ease; pointer-events: none;
            }
        </style>
        <!-- Three.js Library Import -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <div id="game-container">
            <div id="damage-overlay"></div>
            <div id="crosshair"></div>
            <div id="ui-layer">
                <div class="hud">
                    HEALTH: <span id="hp-val" style="color: #ff3333;">100</span> | 
                    SCORE: <span id="score-val">0</span>
                </div>
                <div class="hud" id="status-msg" style="font-size: 16px; color: #aaa;">
                    [화면 클릭시 사격 모드 진입]
                </div>
            </div>

            <div id="blocker">
                <h1 style="font-size: 40px; margin-bottom: 10px;">클릭하여 전투 시작</h1>
                <p>W, A, S, D: 이동 | 마우스: 시야 조작 | 좌클릭: 발사</p>
            </div>
        </div>

        <script>
            // --- 1. 기본 변수 및 씬 설정 ---
            let scene, camera, renderer;
            let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
            let prevTime = performance.now();
            const velocity = new THREE.Vector3();
            const direction = new THREE.Vector3();

            let playerHP = 100;
            let score = 0;
            let isDead = false;

            // 적 관련 변수
            let enemy;
            let enemyHP = 100;
            let lastEnemyAttack = 0;

            const blocker = document.getElementById('blocker');
            const hpVal = document.getElementById('hp-val');
            const scoreVal = document.getElementById('score-val');
            const damageOverlay = document.getElementById('damage-overlay');

            init();
            animate();

            function init() {
                // Scene & Camera
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x1a1a1a);
                scene.fog = new THREE.Fog(0x1a1a1a, 0, 50);

                camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.y = 1.6; // 플레이어 눈높이

                // Lighting
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
                scene.add(ambientLight);
                const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
                dirLight.position.set(10, 20, 10);
                scene.add(dirLight);

                // 바닥 (Grid)
                const gridHelper = new THREE.GridHelper(60, 60, 0x00ffcc, 0x444444);
                scene.add(gridHelper);

                // Pointer Lock (마우스 가두기 시점 조작)
                blocker.addEventListener('click', function () {
                    if(!isDead) {
                        document.body.requestPointerLock();
                    }
                });

                document.addEventListener('pointerlockchange', function () {
                    if (document.pointerLockElement === document.body) {
                        blocker.style.display = 'none';
                    } else {
                        if(!isDead) blocker.style.display = 'flex';
                    }
                });

                // 키보드 컨트롤 이벤트
                const onKeyDown = function (event) {
                    switch (event.code) {
                        case 'KeyW': moveForward = true; break;
                        case 'KeyA': moveLeft = true; break;
                        case 'KeyS': moveBackward = true; break;
                        case 'KeyD': moveRight = true; break;
                    }
                };

                const onKeyUp = function (event) {
                    switch (event.code) {
                        case 'KeyW': moveForward = false; break;
                        case 'KeyA': moveLeft = false; break;
                        case 'KeyS': moveBackward = false; break;
                        case 'KeyD': moveRight = false; break;
                    }
                };

                document.addEventListener('keydown', onKeyDown);
                document.addEventListener('keyup', onKeyUp);

                // 마우스 회전 컨트롤
                document.addEventListener('mousemove', function (event) {
                    if (document.pointerLockElement === document.body && !isDead) {
                        const movementX = event.movementX || 0;
                        const movementY = event.movementY || 0;

                        camera.rotation.y -= movementX * 0.002;
                        
                        // 상하 시야각 제한
                        let newX = camera.rotation.x - movementY * 0.002;
                        camera.rotation.x = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, newX));
                    }
                });

                // 사격 처리 (마우스 좌클릭)
                document.addEventListener('mousedown', function (event) {
                    if (document.pointerLockElement === document.body && event.button === 0 && !isDead) {
                        shoot();
                    }
                });

                // Renderer
                renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.getElementById('game-container').appendChild(renderer.domElement);

                // 최초 적 생성
                spawnEnemy();

                window.addEventListener('resize', onWindowResize);
            }

            // --- 2. 적(Enemy) 메카닉 ---
            function spawnEnemy() {
                if (enemy) scene.remove(enemy);

                // 메쉬 그룹 생성
                enemy = new THREE.Group();

                // 몸통
                const bodyGeo = new THREE.BoxGeometry(0.8, 1.2, 0.4);
                const bodyMat = new THREE.MeshLambertMaterial({ color: 0xd9534f });
                const body = new THREE.Mesh(bodyGeo, bodyMat);
                body.position.y = 0.6;
                body.name = "body";
                enemy.add(body);

                // 머리 (헤드샷 판정용)
                const headGeo = new THREE.BoxGeometry(0.4, 0.4, 0.4);
                const headMat = new THREE.MeshLambertMaterial({ color: 0xffad99 });
                const head = new THREE.Mesh(headGeo, headMat);
                head.position.y = 1.4;
                head.name = "head";
                enemy.add(head);

                // 스폰 위치 지정 (무작위)
                const angle = Math.random() * Math.PI * 2;
                const distance = 8 + Math.random() * 12; // 8m ~ 20m 거리
                enemy.position.x = Math.cos(angle) * distance;
                enemy.position.z = Math.sin(angle) * distance;

                enemyHP = 100;
                scene.add(enemy);
            }

            // --- 3. 사격 및 피격 판정 (Raycasting) ---
            function shoot() {
                const raycaster = new THREE.Raycaster();
                // 카메라 정중앙 시선 방향으로 레이 발사
                raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);

                const intersects = raycaster.intersectObjects(enemy.children);

                if (intersects.length > 0) {
                    const hitObj = intersects[0].object;
                    let damage = 35; // 몸통 기본 대미지

                    if (hitObj.name === "head") {
                        damage = 100; // 헤드샷 즉사 대미지
                    }

                    enemyHP -= damage;

                    // 적 피격 시각 피드백 (잠시 하얗게)
                    hitObj.material.color.setHex(0xffffff);
                    setTimeout(() => {
                        if (hitObj.name === "head") hitObj.material.color.setHex(0xffad99);
                        else hitObj.material.color.setHex(0xd9534f);
                    }, 80);

                    // 적 처치
                    if (enemyHP <= 0) {
                        score += 100;
                        scoreVal.innerText = score;
                        spawnEnemy();
                    }
                }
            }

            // --- 4. 루프 및 로직 업데이트 ---
            function animate() {
                requestAnimationFrame(animate);

                const time = performance.now();
                const delta = (time - prevTime) / 1000;
                prevTime = time;

                if (document.pointerLockElement === document.body && !isDead) {
                    // 이동 속도 계산
                    velocity.x -= velocity.x * 10.0 * delta;
                    velocity.z -= velocity.z * 10.0 * delta;

                    direction.z = Number(moveForward) - Number(moveBackward);
                    direction.x = Number(moveRight) - Number(moveLeft);
                    direction.normalize();

                    if (moveForward || moveBackward) velocity.z -= direction.z * 50.0 * delta;
                    if (moveLeft || moveRight) velocity.x -= direction.x * 50.0 * delta;

                    // 이동 방향 반영
                    camera.translateX(-velocity.x * delta);
                    camera.translateZ(velocity.z * delta);
                    camera.position.y = 1.6; // Y축 고정

                    // 적의 자동 공격 제어 (1.5초 주기)
                    if (enemy && time - lastEnemyAttack > 1500) {
                        const dist = camera.position.distanceTo(enemy.position);
                        if (dist < 25) { // 사거리 내 위치
                            playerHP -= 15; // 적 공격 대미지
                            hpVal.innerText = playerHP;
                            
                            // 피격 데미지 효과 연출
                            damageOverlay.style.opacity = '1';
                            setTimeout(() => { damageOverlay.style.opacity = '0'; }, 150);

                            if (playerHP <= 0) {
                                isDead = true;
                                hpVal.innerText = 0;
                                document.exitPointerLock();
                                blocker.innerHTML = '<h1 style="color:red;">GAME OVER</h1><p>새로고침 하거나 메뉴로 나가세요.</p>';
                                blocker.style.display = 'flex';
                            }
                        }
                        lastEnemyAttack = time;
                    }

                    // 적이 항상 플레이어를 바라보도록 회전
                    if (enemy) {
                        enemy.lookAt(camera.position.x, enemy.position.y, camera.position.z);
                    }
                }

                renderer.render(scene, camera);
            }

            function onWindowResize() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }
        </script>
    </body>
    </html>

    # Streamlit에 3D 캔버스 임베딩
    components.html(game_html, height=720)
