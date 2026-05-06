FROM node:18-alpine

# Tạo thư mục app trong container
WORKDIR /usr/src/app

# Copy package.json và package-lock.json (nếu có)
COPY package*.json ./

# Cài đặt các thư viện (chỉ cài dependencies cho production)
RUN npm install --only=production

# Copy toàn bộ mã nguồn
COPY . .

# Expose port (port mặc định của app, khớp với ENV PORT nếu có)
EXPOSE 3000

# Chạy ứng dụng
CMD ["npm", "start"]
