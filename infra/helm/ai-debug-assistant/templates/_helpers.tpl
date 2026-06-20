{{- define "ai-debug-assistant.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ai-debug-assistant.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- include "ai-debug-assistant.name" . -}}
{{- end -}}
{{- end -}}

{{- define "ai-debug-assistant.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{- define "ai-debug-assistant.labels" -}}
helm.sh/chart: {{ include "ai-debug-assistant.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/name: {{ include "ai-debug-assistant.name" . }}
{{- end -}}

{{- define "ai-debug-assistant.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/name: {{ include "ai-debug-assistant.name" . }}
{{- end -}}

{{- define "ai-debug-assistant.apiName" -}}
{{- printf "%s-api" (include "ai-debug-assistant.fullname" .) -}}
{{- end -}}

{{- define "ai-debug-assistant.workerName" -}}
{{- printf "%s-worker" (include "ai-debug-assistant.fullname" .) -}}
{{- end -}}

{{- define "ai-debug-assistant.postgresName" -}}
{{- printf "%s-postgres" (include "ai-debug-assistant.fullname" .) -}}
{{- end -}}

{{- define "ai-debug-assistant.redisName" -}}
{{- printf "%s-redis" (include "ai-debug-assistant.fullname" .) -}}
{{- end -}}

{{- define "ai-debug-assistant.configName" -}}
{{- printf "%s-config" (include "ai-debug-assistant.fullname" .) -}}
{{- end -}}

{{- define "ai-debug-assistant.secretName" -}}
{{- printf "%s-secrets" (include "ai-debug-assistant.fullname" .) -}}
{{- end -}}

{{- define "ai-debug-assistant.databaseUrl" -}}
{{- if .Values.postgres.enabled -}}
{{- printf "postgresql+psycopg://%s:%s@%s:5432/%s" .Values.postgres.user .Values.postgres.password (include "ai-debug-assistant.postgresName" .) .Values.postgres.database -}}
{{- else -}}
{{- required "external.databaseUrl is required when postgres.enabled=false" .Values.external.databaseUrl -}}
{{- end -}}
{{- end -}}

{{- define "ai-debug-assistant.redisUrl" -}}
{{- if .Values.redis.enabled -}}
{{- printf "redis://%s:6379/0" (include "ai-debug-assistant.redisName" .) -}}
{{- else -}}
{{- required "external.redisUrl is required when redis.enabled=false" .Values.external.redisUrl -}}
{{- end -}}
{{- end -}}
