#!/usr/bin/env groovy

@Library('lco-shared-libs@master') _

pipeline {
	agent any
	stages {
		stage('Build image') {
			steps {
				sh 'make docker-build'
			}
		}
		stage('Push image') {
			steps {
				sh 'make docker-push'
			}
		}
	}
	post {
		always { postBuildNotify() }
	}
}
