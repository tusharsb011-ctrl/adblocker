/**
 * RESTful API Routes
 * Provides endpoints for DNS Filter Dashboard
 */

const express = require('express');
const router = express.Router();
const db = require('../db/database');

/**
 * GET /api/stats
 * Returns dashboard statistics
 */
router.get('/stats', (req, res) => {
    try {
        const stats = db.getStats();
        res.json(stats);
    } catch (error) {
        console.error('Stats error:', error.message);
        res.status(500).json({ error: 'Failed to fetch statistics' });
    }
});

/**
 * GET /api/top-blocked
 * Returns top blocked domains with query counts
 * @query {number} limit - Maximum results (default: 10)
 */
router.get('/top-blocked', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 10;
        const topBlocked = db.getTopBlocked(limit);
        res.json(topBlocked);
    } catch (error) {
        console.error('Top blocked error:', error.message);
        res.json([]);
    }
});

/**
 * GET /api/logs/blocked
 * Returns recent blocked query logs
 * @query {number} limit - Maximum results (default: 100)
 */
router.get('/logs/blocked', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 100;
        const logs = db.getBlockedLogs(limit);
        res.json(logs);
    } catch (error) {
        console.error('Blocked logs error:', error.message);
        res.json([]);
    }
});

/**
 * GET /api/logs/allowed
 * Returns recent allowed query logs
 * @query {number} limit - Maximum results (default: 100)
 */
router.get('/logs/allowed', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 100;
        const logs = db.getAllowedLogs(limit);
        res.json(logs);
    } catch (error) {
        console.error('Allowed logs error:', error.message);
        res.json([]);
    }
});

/**
 * GET /api/domains
 * Returns list of all blocked domains
 * @query {number} limit - Maximum results (default: 1000)
 */
router.get('/domains', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 1000;
        const domains = db.getAllDomains(limit);
        res.json(domains);
    } catch (error) {
        console.error('Domains error:', error.message);
        res.json([]);
    }
});

module.exports = router;
