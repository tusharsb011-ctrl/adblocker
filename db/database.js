/**
 * Database Connection Layer
 * Handles SQLite database connection and provides query helpers
 * Using sql.js (pure JavaScript SQLite implementation)
 */

const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

// Database file path
const DB_PATH = path.join(__dirname, '..', 'database', 'dns_filter.db');

let db = null;
let dbReady = false;

/**
 * Initialize database connection
 * @returns {Promise<Database>} SQLite database instance
 */
async function initDatabase() {
    if (db && dbReady) {
        return db;
    }

    try {
        const SQL = await initSqlJs();

        // Read the database file
        const buffer = fs.readFileSync(DB_PATH);
        db = new SQL.Database(buffer);
        dbReady = true;

        console.log('✅ Connected to SQLite database');
        return db;
    } catch (error) {
        console.error('❌ Database connection failed:', error.message);
        throw error;
    }
}

/**
 * Get the database instance (must call initDatabase first)
 * @returns {Database} SQLite database instance
 */
function getDatabase() {
    if (!db || !dbReady) {
        throw new Error('Database not initialized. Call initDatabase() first.');
    }
    return db;
}

/**
 * Execute a query and return all results
 * @param {string} sql - SQL query
 * @param {Array} params - Query parameters
 * @returns {Array} Array of result objects
 */
function queryAll(sql, params = []) {
    const database = getDatabase();
    const stmt = database.prepare(sql);
    stmt.bind(params);

    const results = [];
    while (stmt.step()) {
        const row = stmt.getAsObject();
        results.push(row);
    }
    stmt.free();

    return results;
}

/**
 * Execute a query and return single result
 * @param {string} sql - SQL query
 * @param {Array} params - Query parameters
 * @returns {Object|null} Single result object or null
 */
function queryOne(sql, params = []) {
    const database = getDatabase();
    const stmt = database.prepare(sql);
    stmt.bind(params);

    let result = null;
    if (stmt.step()) {
        result = stmt.getAsObject();
    }
    stmt.free();

    return result;
}

/**
 * Get dashboard statistics
 * @returns {Object} Statistics object with counts
 */
function getStats() {
    const totalBlocked = queryOne('SELECT COUNT(*) as count FROM blocked');
    const blockedQueries = queryOne("SELECT COUNT(*) as count FROM queries WHERE action='blocked'");
    const allowedQueries = queryOne("SELECT COUNT(*) as count FROM queries WHERE action='allowed'");

    return {
        total_blocked_domains: totalBlocked ? totalBlocked.count : 0,
        blocked_queries: blockedQueries ? blockedQueries.count : 0,
        allowed_queries: allowedQueries ? allowedQueries.count : 0,
        total_queries: (blockedQueries ? blockedQueries.count : 0) + (allowedQueries ? allowedQueries.count : 0)
    };
}

/**
 * Get top blocked domains
 * @param {number} limit - Maximum number of results
 * @returns {Array} Array of domain objects with counts
 */
function getTopBlocked(limit = 10) {
    return queryAll(`
        SELECT domain, COUNT(*) as count 
        FROM queries 
        WHERE action='blocked'
        GROUP BY domain 
        ORDER BY count DESC 
        LIMIT ?
    `, [limit]);
}

/**
 * Get blocked query logs
 * @param {number} limit - Maximum number of results
 * @returns {Array} Array of blocked query log entries
 */
function getBlockedLogs(limit = 100) {
    return queryAll(`
        SELECT timestamp, client_ip, domain, query_type 
        FROM queries 
        WHERE action='blocked'
        ORDER BY id DESC 
        LIMIT ?
    `, [limit]);
}

/**
 * Get allowed query logs
 * @param {number} limit - Maximum number of results
 * @returns {Array} Array of allowed query log entries
 */
function getAllowedLogs(limit = 100) {
    return queryAll(`
        SELECT timestamp, client_ip, domain, query_type, response_time 
        FROM queries 
        WHERE action='allowed'
        ORDER BY id DESC 
        LIMIT ?
    `, [limit]);
}

/**
 * Get all blocked domains
 * @param {number} limit - Maximum number of results
 * @returns {Array} Array of domain strings
 */
function getAllDomains(limit = 1000) {
    const rows = queryAll(`
        SELECT domain 
        FROM blocked 
        ORDER BY domain 
        LIMIT ?
    `, [limit]);

    return rows.map(row => row.domain);
}

/**
 * Close database connection
 */
function closeDatabase() {
    if (db) {
        db.close();
        db = null;
        dbReady = false;
        console.log('Database connection closed');
    }
}

module.exports = {
    initDatabase,
    getDatabase,
    getStats,
    getTopBlocked,
    getBlockedLogs,
    getAllowedLogs,
    getAllDomains,
    closeDatabase
};
