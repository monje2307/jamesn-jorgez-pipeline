pipeline {
    agent any

    environment {
        PYTHON       = 'python3'
        APP_MODULE   = 'restaurante'
        TEST_DIR     = '.'
        REPORTS_DIR  = 'reports'
        DIST_DIR     = 'dist'
        VENV         = 'venv'
        MIN_COVERAGE = '85'
    }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }

    stages {

        // ───────────────── CHECKOUT ─────────────────
        stage('Checkout') {
            steps {
                checkout scm
                sh 'mkdir -p reports dist'
            }
        }

        // ───────────────── BUILD ─────────────────
        stage('Build') {
            steps {
                echo '📦 Creando entorno virtual e instalando dependencias'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install pytest pytest-html coverage
                '''
            }
        }

        stage('Build › Validar sintaxis') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m py_compile restaurante.py
                    python -m py_compile test_*.py
                '''
            }
        }

        // ───────────────── TESTS ─────────────────
        stage('Test › Unitarias Menu') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_unitarias_menu.py \
                      --html=reports/menu.html --self-contained-html \
                      --junitxml=reports/menu.xml
                '''
            }
            post {
                always {
                    junit 'reports/menu.xml'
                }
            }
        }

        stage('Test › Unitarias Pedido') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_unitarias_pedido.py \
                      --html=reports/pedido.html --self-contained-html \
                      --junitxml=reports/pedido.xml
                '''
            }
            post {
                always {
                    junit 'reports/pedido.xml'
                }
            }
        }

        stage('Test › Integración') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_integracion.py \
                      --html=reports/integracion.html --self-contained-html \
                      --junitxml=reports/integracion.xml
                '''
            }
            post {
                always {
                    junit 'reports/integracion.xml'
                }
            }
        }

        stage('Test › Regresión') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_regresion.py \
                      --html=reports/regresion.html --self-contained-html \
                      --junitxml=reports/regresion.xml
                '''
            }
            post {
                always {
                    junit 'reports/regresion.xml'
                }
            }
        }

        stage('Test › Cobertura') {
            steps {
                sh '''
                    . venv/bin/activate
                    coverage run -m pytest
                    coverage report --fail-under=85
                    coverage html -d reports/coverage
                '''
            }
        }

        // ───────────────── DEPLOY ─────────────────
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    . venv/bin/activate
                    VERSION=\$(python -c "from restaurante import version; print(version())")
                    echo "Versión desplegada: \$VERSION" > dist/version.txt
                '''
                archiveArtifacts artifacts: 'dist/version.txt', fingerprint: true
            }
        }
    }

    // ───────────────── POST ACCIONES GLOBALES ─────────────────
    post {
        always {
            // Evaluamos si el resultado del pipeline fue exitoso para archivar los reportes antes de limpiar
            script {
                if (currentBuild.currentResult == 'SUCCESS') {
                    echo '📦 Guardando artefactos generados...'
                    archiveArtifacts artifacts: 'reports/**/*', fingerprint: true
                    echo '✅ PIPELINE COMPLETADO CON ÉXITO'
                } else {
                    echo '❌ PIPELINE FALLIDO — revisa los reportes de consola'
                }
            }
            // La limpieza se ejecuta estrictamente al final de todo el flujo
            echo '🧹 Limpiando el espacio de trabajo...'
            cleanWs()
        }
    }
}
