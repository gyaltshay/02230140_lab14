# Purpose: Build three Alpine-based local images from the same application source.
FROM python:3.12-alpine
ARG APP_VERSION=1.0.0
ARG STUDENT_ID=02230140
ENV APP_VERSION=${APP_VERSION} STUDENT_ID=${STUDENT_ID}
RUN addgroup -S notice && adduser -S notice -G notice
WORKDIR /app
COPY app.py ./app.py
EXPOSE 8080
USER notice
CMD ["python", "app.py"]
