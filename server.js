/**
 * DNS Filter Dashboard - Express Server
 * Main entry point for the Node.js application
 */

const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');

// Import routes and database
const apiRoutes = require('./routes/api');
const { initDatabase, closeDatabase } = require('./db/database');

// Create Express app
const app = express();
const PORT = process.env.PORT || 8000;

// ======================
// Middleware
// ======================

// Enable CORS for all origins
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// Parse JSON request bodies
app.use(express.json());

// HTTP request logging
app.use(morgan('dev'));

// ======================
// Static Files
// ======================

// Serve static files from current directory
app.use(express.static(__dirname));

// ======================
// Routes
// ======================

// Mount API routes
app.use('/api', apiRoutes);

// Serve dashboard as the default route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// ======================
// Error Handling
// ======================

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Global error handler
app.use((err, req, res, next) => {
    console.error('Server error:', err.message);
    res.status(500).json({ error: 'Internal server error' });
});

// ======================
// Server Start
// ======================

async function startServer() {
    try {
        // Initialize database first
        await initDatabase();

        app.listen(PORT, () => {
            console.log('\n' + '='.repeat(60));
            console.log('🛡️  DNS FILTER DASHBOARD - Node.js Express Server');
            console.log('='.repeat(60));
            console.log(`📡 Server running at:    http://localhost:${PORT}`);
            console.log(`📊 Dashboard:            http://localhost:${PORT}/`);
            console.log(`🔌 API Base:             http://localhost:${PORT}/api`);
            console.log('='.repeat(60));
            console.log('Press Ctrl+C to stop\n');
        });
    } catch (error) {
        console.error('Failed to start server:', error.message);
        process.exit(1);
    }
}

// Start the server
startServer();

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\n👋 Server shutting down...');
    closeDatabase();
    process.exit(0);
});
