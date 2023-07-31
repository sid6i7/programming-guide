FROM node as builder
WORKDIR /app
COPY ./package.json ./
RUN npm install
COPY . .
ARG REACT_APP_RECOMMEND_ENDPOINT
ARG REACT_APP_API_URL
ENV REACT_APP_RECOMMEND_ENDPOINT /recommend
ENV REACT_APP_API_URL /api
RUN npm run build

FROM nginx
EXPOSE 3000
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/build /usr/share/nginx/html