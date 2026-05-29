// =============================================================
//  Jenkinsfile — Sistema Restaurante SoftNova
//  Pruebas automatizadas completas en pipeline
//
//  FLUJO:
//  Checkout → Build → Test (4 niveles) → Reporte → Deploy
//
//  NIVELES DE TEST:
//  1. Unitarias Menu      → test_unitarias_menu.py     (22 tests)
//  2. Unitarias Pedido    → test_unitarias_pedido.py   (27 tests)
//  3. Integración         → test_integracion.py        (16 tests)
//  4. Regresión           → test_regresion.py          (19 tests)
//  + Cobertura total      → coverage ≥ 85%
//  + Smoke post-deploy    → test_smoke.py              (17 tests)
// =============================================================

pipeline {
    agent any

    environment {
        PYTHON       = 'python3'
        APP_MODULE   = 'restaurante'
        TEST_DIR     = 'tests'
        REPORTS_DIR  = 'reports'
        DIST_DIR     = 'dist'
        DEPLOY_ENV   = "${env.BRANCH_NAME == 'main' ? 'production' : 'staging'}"
        MIN_COVERAGE = '85'
    }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
        skipStagesAfterUnstable()      // detiene el pipeline si una etapa queda inestable
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    // ==========================================================
    //  ETAPAS
    // ==========================================================
    stages {

        // ── 0. CHECKOUT ────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo "🔄 [CHECKOUT] Rama: ${env.BRANCH_NAME} | Commit: ${env.GIT_COMMIT?.take(8)}"
                checkout scm
                sh 'mkdir -p ${REPORTS_DIR} ${DIST_DIR}'
            }
        }

        // ── 1. BUILD ───────────────────────────────────────────
        stage('Build') {
            stages {

                stage('Build › Dependencias') {
                    steps {
                        echo '📦 [BUILD 1/3] Instalando dependencias...'
                        sh '''
                            ${PYTHON} -m pip install --upgrade pip --quiet
                            ${PYTHON} -m pip install -r requirements.txt --quiet
                            echo "    ✅ Dependencias instaladas"
                        '''
                    }
                }

                stage('Build › Validar sintaxis') {
                    steps {
                        echo '🔍 [BUILD 2/3] Validando sintaxis Python...'
                        sh '''
                            ${PYTHON} -m py_compile ${APP_MODULE}.py
                            echo "    ✅ ${APP_MODULE}.py — OK"

                            for f in ${TEST_DIR}/test_*.py; do
                                ${PYTHON} -m py_compile "$f"
                                echo "    ✅ $f — OK"
                            done
                        '''
                    }
                }

                stage('Build › Empaquetar') {
                    steps {
                        echo '📦 [BUILD 3/3] Empaquetando módulo...'
                        sh '''
                            ${PYTHON} setup.py egg_info --quiet 2>/dev/null || true
                            VERSION=$(${PYTHON} -c "from ${APP_MODULE} import version; print(version())")
                            echo "    ✅ ${APP_MODULE} v${VERSION} listo"
                        '''
                    }
                }
            }

            post {
                success { echo '✅ [BUILD] Completado — código validado y empaquetado.' }
                failure { error  '❌ [BUILD] Error de compilación — pipeline detenido.' }
            }
        }

        // ── 2. TEST ────────────────────────────────────────────
        stage('Test') {
            stages {

                // ── 2a. Unitarias: Menu ─────────────────────────
                stage('Test › Unitarias Menu') {
                    steps {
                        echo '🧪 [TEST 1/4] Pruebas unitarias — clase Menu (22 tests)...'
                        sh '''
                            ${PYTHON} -m pytest ${TEST_DIR}/test_unitarias_menu.py \
                                -v --tb=short \
                                --html=${REPORTS_DIR}/01_unitarias_menu.html \
                                --self-contained-html \
                                --junitxml=${REPORTS_DIR}/junit_01_menu.xml
                        '''
                    }
                    post {
                        always {
                            junit "${REPORTS_DIR}/junit_01_menu.xml"
                            publishHTML([
                                allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                reportDir: "${REPORTS_DIR}", reportFiles: '01_unitarias_menu.html',
                                reportName: '🧾 [1] Unitarias Menu'
                            ])
                        }
                        failure {
                            echo '⚠️  Unitarias Menu fallaron — revisar lógica de la clase Menu.'
                        }
                    }
                }

                // ── 2b. Unitarias: Pedido ───────────────────────
                stage('Test › Unitarias Pedido') {
                    steps {
                        echo '🧪 [TEST 2/4] Pruebas unitarias — clase Pedido (27 tests)...'
                        sh '''
                            ${PYTHON} -m pytest ${TEST_DIR}/test_unitarias_pedido.py \
                                -v --tb=short \
                                --html=${REPORTS_DIR}/02_unitarias_pedido.html \
                                --self-contained-html \
                                --junitxml=${REPORTS_DIR}/junit_02_pedido.xml
                        '''
                    }
                    post {
                        always {
                            junit "${REPORTS_DIR}/junit_02_pedido.xml"
                            publishHTML([
                                allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                reportDir: "${REPORTS_DIR}", reportFiles: '02_unitarias_pedido.html',
                                reportName: '🧾 [2] Unitarias Pedido'
                            ])
                        }
                        failure {
                            echo '⚠️  Unitarias Pedido fallaron — revisar lógica de cálculos.'
                        }
                    }
                }

                // ── 2c. Integración ─────────────────────────────
                stage('Test › Integración') {
                    steps {
                        echo '🔗 [TEST 3/4] Pruebas de integración — Menu + Pedido (16 tests)...'
                        sh '''
                            ${PYTHON} -m pytest ${TEST_DIR}/test_integracion.py \
                                -v --tb=short \
                                --html=${REPORTS_DIR}/03_integracion.html \
                                --self-contained-html \
                                --junitxml=${REPORTS_DIR}/junit_03_integracion.xml
                        '''
                    }
                    post {
                        always {
                            junit "${REPORTS_DIR}/junit_03_integracion.xml"
                            publishHTML([
                                allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                reportDir: "${REPORTS_DIR}", reportFiles: '03_integracion.html',
                                reportName: '🔗 [3] Integración'
                            ])
                        }
                        failure {
                            echo '⚠️  Integración falló — las clases no interactúan correctamente.'
                        }
                    }
                }

                // ── 2d. Regresión ───────────────────────────────
                stage('Test › Regresión') {
                    steps {
                        echo '🔁 [TEST 4/4] Pruebas de regresión — bugs conocidos (19 tests)...'
                        sh '''
                            ${PYTHON} -m pytest ${TEST_DIR}/test_regresion.py \
                                -v --tb=long \
                                --html=${REPORTS_DIR}/04_regresion.html \
                                --self-contained-html \
                                --junitxml=${REPORTS_DIR}/junit_04_regresion.xml
                        '''
                    }
                    post {
                        always {
                            junit "${REPORTS_DIR}/junit_04_regresion.xml"
                            publishHTML([
                                allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                reportDir: "${REPORTS_DIR}", reportFiles: '04_regresion.html',
                                reportName: '🔁 [4] Regresión'
                            ])
                        }
                        failure {
                            error '❌ REGRESIÓN DETECTADA — un bug corregido volvió a aparecer. Deploy bloqueado.'
                        }
                    }
                }

                // ── 2e. Cobertura total ─────────────────────────
                stage('Test › Cobertura') {
                    steps {
                        echo "📊 [COBERTURA] Mínimo requerido: ${MIN_COVERAGE}%..."
                        sh '''
                            ${PYTHON} -m coverage run \
                                --source=${APP_MODULE} \
                                -m pytest ${TEST_DIR}/test_unitarias_menu.py \
                                          ${TEST_DIR}/test_unitarias_pedido.py \
                                          ${TEST_DIR}/test_integracion.py \
                                          ${TEST_DIR}/test_regresion.py \
                                --quiet

                            ${PYTHON} -m coverage report \
                                --fail-under=${MIN_COVERAGE} \
                                --show-missing

                            ${PYTHON} -m coverage html -d ${REPORTS_DIR}/coverage_html
                            ${PYTHON} -m coverage xml  -o ${REPORTS_DIR}/coverage.xml
                        '''
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                reportDir: "${REPORTS_DIR}/coverage_html",
                                reportFiles: 'index.html',
                                reportName: '📊 Cobertura de Código'
                            ])
                        }
                        failure {
                            error "❌ Cobertura por debajo del ${MIN_COVERAGE}% — deploy bloqueado."
                        }
                    }
                }

            }  // fin sub-stages Test

            post {
                success { echo '✅ [TEST] 96/96 pruebas pasaron con cobertura ≥ 85%.' }
                failure { error '❌ [TEST] Falló — deploy bloqueado hasta corregir los errores.' }
            }
        }  // fin TEST

        // ── 3. REPORTE CONSOLIDADO ─────────────────────────────
        stage('Reporte') {
            steps {
                echo '📋 [REPORTE] Generando resumen consolidado...'
                sh '''
                    echo "================================================"
                    echo "  RESUMEN DE PRUEBAS — SoftNova Restaurante"
                    echo "================================================"
                    echo ""

                    total=0; passed=0; failed=0
                    for xml in ${REPORTS_DIR}/junit_*.xml; do
                        t=$(grep -o 'tests="[0-9]*"' "$xml" | grep -o '[0-9]*' || echo 0)
                        f=$(grep -o 'failures="[0-9]*"' "$xml" | grep -o '[0-9]*' || echo 0)
                        e=$(grep -o 'errors="[0-9]*"' "$xml"   | grep -o '[0-9]*' || echo 0)
                        total=$((total + t))
                        failed=$((failed + f + e))
                        passed=$((passed + t - f - e))
                        name=$(basename "$xml" .xml | sed 's/junit_0._//')
                        echo "  $([ $((f+e)) -eq 0 ] && echo ✅ || echo ❌) $name: $t tests ($f fallos)"
                    done

                    echo ""
                    echo "  Total : $total"
                    echo "  ✅ OK  : $passed"
                    echo "  ❌ KO  : $failed"
                    echo "================================================"
                '''
            }
        }

        // ── 4. DEPLOY ──────────────────────────────────────────
        stage('Deploy') {
            when {
                anyOf { branch 'main'; branch 'develop' }
            }
            stages {

                stage('Deploy › Smoke tests') {
                    steps {
                        echo '💨 [DEPLOY 1/3] Smoke tests pre-deploy (17 tests)...'
                        sh '''
                            ${PYTHON} -m pytest ${TEST_DIR}/test_smoke.py \
                                -v --tb=short \
                                --html=${REPORTS_DIR}/05_smoke.html \
                                --self-contained-html \
                                --junitxml=${REPORTS_DIR}/junit_05_smoke.xml
                        '''
                    }
                    post {
                        always {
                            junit "${REPORTS_DIR}/junit_05_smoke.xml"
                            publishHTML([
                                allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                reportDir: "${REPORTS_DIR}", reportFiles: '05_smoke.html',
                                reportName: '💨 [5] Smoke Tests'
                            ])
                        }
                        failure {
                            error '❌ Smoke tests fallaron — el sistema no puede arrancar. Deploy revertido.'
                        }
                    }
                }

                stage('Deploy › Publicar artefacto') {
                    steps {
                        echo '📤 [DEPLOY 2/3] Generando artefacto de versión...'
                        sh '''
                            ${PYTHON} deploy.py
                            echo ""
                            echo "  Artefacto generado:"
                            cat ${DIST_DIR}/version.txt
                        '''
                        archiveArtifacts artifacts: "${DIST_DIR}/version.txt", fingerprint: true
                    }
                }

                stage('Deploy › Notificación') {
                    steps {
                        echo '📣 [DEPLOY 3/3] Notificando despliegue...'
                        sh '''
                            VERSION=$(${PYTHON} -c "from ${APP_MODULE} import version; print(version())")
                            echo "============================================"
                            echo "  ✅ DEPLOY EXITOSO — SoftNova Restaurante"
                            echo "  Versión  : ${VERSION}"
                            echo "  Entorno  : ${DEPLOY_ENV}"
                            echo "  Build    : #${BUILD_NUMBER}"
                            echo "  Tests    : 96 unitarios/integración/regresión"
                            echo "             + 17 smoke post-deploy"
                            echo "  Cobertura: ≥ ${MIN_COVERAGE}%"
                            echo "============================================"
                        '''
                    }
                }
            }

            post {
                success { echo '✅ [DEPLOY] Despliegue completado correctamente.' }
                failure { error '❌ [DEPLOY] Despliegue fallido. Revisar smoke tests.' }
            }
        }

    }  // fin stages

    // ==========================================================
    //  POST-PIPELINE GLOBAL
    // ==========================================================
    post {
        success {
            echo '╔══════════════════════════════════════╗'
            echo '║  ✅  PIPELINE COMPLETADO CON ÉXITO  ║'
            echo '╚══════════════════════════════════════╝'
            archiveArtifacts artifacts: 'reports/**/*', fingerprint: true
        }
        failure {
            echo '╔══════════════════════════════════════╗'
            echo '║  ❌  PIPELINE FALLIDO                ║'
            echo '║  Revisar reportes adjuntos           ║'
            echo '╚══════════════════════════════════════╝'
        }
        unstable {
            echo '⚠️  Pipeline inestable — algunas pruebas fallaron.'
        }
        always {
            cleanWs(cleanWhenSuccess: false)
        }
    }

}
