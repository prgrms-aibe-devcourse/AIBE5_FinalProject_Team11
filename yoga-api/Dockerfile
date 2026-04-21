# Stage 1: build
FROM maven:3.9-eclipse-temurin-17-alpine AS build
WORKDIR /app

COPY pom.xml .
# Pre-fetch dependencies separately so this layer is cached
RUN mvn -q dependency:go-offline -B

COPY src ./src
RUN mvn -q -DskipTests package -B

# Stage 2: run
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

COPY --from=build /app/target/yoga-api-*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
