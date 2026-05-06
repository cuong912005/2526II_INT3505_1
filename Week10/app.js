const express = require('express');
const winston = require('winston');
const promClient = require('prom-client');
const rateLimit = require('express-rate-limit');

const app = express();
const port = process.env.PORT || 3000;

// 1. Cài đặt Logging với Winston
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.Console(),
        // Có thể lưu log ra file trong production
        // new winston.transports.File({ filename: 'error.log', level: 'error' }),
        // new winston.transports.File({ filename: 'combined.log' })
    ]
});

// Middleware log request
app.use((req, res, next) => {
    logger.info(`Incoming request: ${req.method} ${req.url}`);
    next();
});

// 2. Cài đặt Monitoring với Prometheus
const collectDefaultMetrics = promClient.collectDefaultMetrics;
collectDefaultMetrics({ register: promClient.register });

const httpRequestDurationMicroseconds = new promClient.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'code'],
    buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

app.use((req, res, next) => {
    const end = httpRequestDurationMicroseconds.startTimer();
    res.on('finish', () => {
        end({ method: req.method, route: req.route ? req.route.path : req.path, code: res.statusCode });
    });
    next();
});

// 3. Thiết lập Rate Limiting
const apiLimiter = rateLimit({
    windowMs: 1 * 60 * 1000, // 1 phút
    max: 5, // Giới hạn 5 request / 1 phút / IP để dễ test
    message: {
        status: 429,
        error: 'Too many requests',
        message: 'Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau 1 phút.'
    },
    standardHeaders: true, 
    legacyHeaders: false,
});

// Chỉ áp dụng rate limit cho các endpoint /api/
app.use('/api/', apiLimiter);

// Routes
app.get('/', (req, res) => {
    res.send('Week 10: Service Operation – Security & Monitoring');
});

app.get('/api/data', (req, res) => {
    logger.info('Accessed /api/data endpoint');
    res.json({ message: 'Đây là dữ liệu từ API đã được bảo vệ bởi Rate Limit' });
});

// Endpoint cho Prometheus scraper
app.get('/metrics', async (req, res) => {
    res.set('Content-Type', promClient.register.contentType);
    res.end(await promClient.register.metrics());
});

app.listen(port, () => {
    logger.info(`Server đang chạy tại http://localhost:${port}`);
    logger.info(`API endpoint: http://localhost:${port}/api/data`);
    logger.info(`Metrics endpoint: http://localhost:${port}/metrics`);
});
