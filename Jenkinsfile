binary_size_suffix = ['mini':'', 'huge':'_huge']

def convertToNativePath(path) {
    if(!isUnix())
        return path.replaceAll('/','\\\\')
    else
        return path
}

def getOSName() {
    uname  = sh(returnStdout: true, script: 'python -c "import platform; print(platform.system())"').trim()
    os_map = ['Linux':'linux', 'Darwin':'mac', 'Windows':'win']

    return os_map[uname]
}

def getJobType() {
    def causes = "${currentBuild.rawBuild.getCauses()}"
    def job_type = "UNKNOWN"
    
    if(causes ==~ /.*TimerTrigger.*/)    { job_type = "cron" }
    if(causes ==~ /.*GitHubPushCause.*/) { job_type = "push" }
    if(causes ==~ /.*UserIdCause.*/)     { job_type = "manual" }
    if(causes ==~ /.*ReplayCause.*/)     { job_type = "manual" }
    
    return job_type
}

def isMasterBranch() {
    return GIT_BRANCH_SHORT == "master" || GIT_BRANCH_SHORT == "master-dev"
}

def isReleaseBranch() {
    return GIT_BRANCH_SHORT ==~ /release.*/
}

// Can't be called to set pipeline envvars, because depends on CI_BUILD
def isContinuousBuild() {
    return (CI_BUILD == "1" && isMasterBranch()) || isReleaseBranch() || JOB_TYPE == "cron"
}

// Can't be called to set pipeline envvars, because depends on CI_BUILD
def isExperimentalBuild() {
    return CI_BUILD == "1" && !(isMasterBranch() || isReleaseBranch())
}

// Can't be called to set pipeline envvars, because depends on CI_BUILD indirectly
def isBinaryBuild() {
    return isContinuousBuild() || isExperimentalBuild()
}

def getBuildStabilityType() {
    if(isContinuousBuild())        return 'unstable'
    else if(isExperimentalBuild()) return 'experimental'
    else                           return 'NONE'
}

def getInstallerExt() {
    if(isUnix()) return 'sh'
    else         return 'exe'
}

def getDeployFileName(size_type) {
    stability_type = getBuildStabilityType()
    installer_ext  = getInstallerExt()

    return "eman2_sphire_sparx"+ binary_size_suffix[size_type] + ".${AGENT_OS_NAME}." + stability_type + "." + installer_ext
}

def testPackage(installer_file, installation_dir) {
    def script_file_base = convertToNativePath("tests/test_binary_installation.")
    installer_file       = convertToNativePath(installer_file)
    installation_dir     = convertToNativePath(installation_dir)
    
    if(isUnix())
        sh  "bash " + script_file_base + "sh "  + installer_file + " " + installation_dir
    else
        bat "call " + script_file_base + "bat " + installer_file + " " + installation_dir
}

def deployPackage(size_type='') {
    stability_type = getBuildStabilityType()
    installer_ext  = getInstallerExt()

    def sourceFile  = "eman2" + binary_size_suffix[size_type] + ".${AGENT_OS_NAME}." + installer_ext
    def targetFile  = getDeployFileName(size_type)
    def cdCommand   = "cd ${DEPLOY_PATH}/" + stability_type
    def mvCommand   = "mv " + sourceFile + " " + targetFile
    def execCommand = cdCommand + " && " + mvCommand
    
    sshPublisher(publishers: [
                              sshPublisherDesc(configName: 'Installer-Server',
                                               transfers:
                                                          [sshTransfer(sourceFiles:        sourceFile,
                                                                       removePrefix:       "",
                                                                       remoteDirectory:    stability_type,
                                                                       remoteDirectorySDF: false,
                                                                       cleanRemote:        false,
                                                                       excludes:           '',
                                                                       execCommand:        execCommand,
                                                                       execTimeout:        120000,
                                                                       flatten:            false,
                                                                       makeEmptyDirs:      false,
                                                                       noDefaultExcludes:  false,
                                                                       patternSeparator:   '[, ]+'
                                                                      )
                                                          ],
                                                          usePromotionTimestamp:   false,
                                                          useWorkspaceInPromotion: false,
                                                          verbose:                 true
                                              )
                             ]
                )
}

def testDeployedPackage(size_type) {
    stability_type = getBuildStabilityType()

    def file_name = getDeployFileName(size_type)
    def download_dir = "${HOME_DIR}/workspace/jenkins-continuous-download/"

    fileOperations([fileDownloadOperation(url: 'https://cryoem.bcm.edu/cryoem/static/software/' + stability_type + "/" + file_name,
                                          targetLocation: download_dir,
                                          targetFileName: file_name,
                                          userName: '',
                                          password: ''
                                          )])
    
    testPackage(download_dir + file_name, download_dir + size_type)
}

// For debugging purposes
def isSkipStage() {
//     return 0
//     return NODE_NAME != "linux-1"
//     return AGENT_OS_NAME != "mac"
//     return STAGE_NAME != "package"
// 
    stages = [
        'build-local',
//         'build-recipe',
//         'package',
//         'test-package',
//         'deploy',
//         'test-continuous'
    ]
    return stages.contains(STAGE_NAME) || (AGENT_OS_NAME == "win" && (STAGE_NAME == 'test-package' || STAGE_NAME == 'test-continuous'))
}

pipeline {
  agent {
    node { label "${AGENT_NAME}" }
  }
  
  options {
    timestamps()
    lock resource: "${AGENT_NAME}"
  }
  
  environment {
    AGENT_OS_NAME = getOSName()
    JOB_TYPE = getJobType()
    GIT_BRANCH_SHORT = sh(returnStdout: true, script: 'echo ${GIT_BRANCH##origin/}').trim()
    GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'echo ${GIT_COMMIT:0:7}').trim()
    GIT_AUTHOR_EMAIL = sh(returnStdout: true, script: 'git log -1 --format="%ae"').trim()
    GIT_MESSAGE_SHORT = sprintf("%-30s",sh(returnStdout: true, script: 'git log -1 --format="%s"')).substring(0,30)
    INSTALLERS_DIR = convertToNativePath("${HOME_DIR}/workspace/jenkins-eman-installers")

    CI_BUILD       = sh(script: "! git log -1 | grep '.*\\[ci build\\].*'",       returnStatus: true)
  }
  
  stages {
    stage('init') {
      options { timeout(time: 10, unit: 'MINUTES') }
      
      steps {
        script {
            currentBuild.displayName = currentBuild.displayName + " - ${NODE_NAME}"
            currentBuild.description = "${GIT_COMMIT_SHORT}: ${GIT_MESSAGE_SHORT}"
        }
        sh 'env | sort'
      }
    }
    
    stage('build-local') {
      when {
        not { expression { isBinaryBuild() } }
        expression { isUnix() }
        not { expression { isSkipStage() } }
      }
      
      steps {
        sh 'source ci_support/set_env_vars.sh && source $(conda info --root)/bin/activate eman-deps-${EMAN_DEPS_VERSION} && env | sort && bash ci_support/build_no_recipe.sh'
      }
    }
    
    stage('build-recipe') {
      when { not { expression { isSkipStage() } } }
      steps {
        sh 'source ci_support/set_env_vars.sh && bash ci_support/build_recipe.sh'
      }
    }
    
    stage('package') {
      when {
        expression { isBinaryBuild() }
        not { expression { isSkipStage() } }
      }
      environment { PARENT_STAGE_NAME = "${STAGE_NAME}" }
      
      parallel {
        stage('mini')   { steps { sh "bash ci_support/package.sh " + '${WORKSPACE} ${WORKSPACE}/ci_support/constructor-${STAGE_NAME}/' } }
        stage('huge')   { steps { sh "bash ci_support/package.sh " + '${WORKSPACE} ${WORKSPACE}/ci_support/constructor-${STAGE_NAME}/' } }
      }
    }
    
    stage('test-package') {
      when {
        expression { isBinaryBuild() }
        not { expression { isSkipStage() } }
      }
      environment {
        PARENT_STAGE_NAME = "${STAGE_NAME}"
        INSTALLER_EXT     = getInstallerExt()
      }
      
      parallel {
        stage('mini')   { steps { testPackage("${WORKSPACE}/eman2" + binary_size_suffix[STAGE_NAME] + ".${AGENT_OS_NAME}.${INSTALLER_EXT}", "${INSTALLERS_DIR}/" + STAGE_NAME) } }
        stage('huge')   { steps { testPackage("${WORKSPACE}/eman2" + binary_size_suffix[STAGE_NAME] + ".${AGENT_OS_NAME}.${INSTALLER_EXT}", "${INSTALLERS_DIR}/" + STAGE_NAME) } }
      }
    }
    
    stage('deploy') {
      when {
        expression { isBinaryBuild() }
        not { expression { isSkipStage() } }
      }
      environment { PARENT_STAGE_NAME = "${STAGE_NAME}" }

      parallel {
        stage('mini')   { steps { deployPackage(STAGE_NAME) } }
        stage('huge')   { steps { deployPackage(STAGE_NAME) } }
      }
    }

    stage('test-continuous') {
      when {
        expression { isBinaryBuild() }
        not { expression { isSkipStage() } }
      }
      environment { PARENT_STAGE_NAME = "${STAGE_NAME}" }

      parallel {
        stage('mini') {
          steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                testDeployedPackage(STAGE_NAME)
            }
          }
        }

        stage('huge') {
          when { expression { AGENT_OS_NAME != 'linux' } }
          steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                testDeployedPackage(STAGE_NAME)
            }
          }
        }
      }
    }
  }
}
