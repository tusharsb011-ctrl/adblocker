package com.dnsfilter.db;

import com.mongodb.MongoClient;
import com.mongodb.MongoClientURI;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.model.Sorts;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Accumulators;
import org.bson.Document;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * MongoDB Database Manager
 * Handles all database operations for DNS Filter Dashboard
 */
public class MongoDBManager {
    
    private static MongoDBManager instance;
    private MongoClient mongoClient;
    private MongoDatabase database;
    
    // MongoDB Configuration
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "dns_filter";
    
    // Collection names
    private static final String BLOCKED_COLLECTION = "blocked";
    private static final String QUERIES_COLLECTION = "queries";
    
    /**
     * Private constructor for singleton pattern
     */
    private MongoDBManager() {
        try {
            MongoClientURI uri = new MongoClientURI(CONNECTION_STRING);
            mongoClient = new MongoClient(uri);
            database = mongoClient.getDatabase(DATABASE_NAME);
            System.out.println("✅ Connected to MongoDB: " + DATABASE_NAME);
        } catch (Exception e) {
            System.err.println("❌ MongoDB connection failed: " + e.getMessage());
        }
    }
    
    /**
     * Get singleton instance
     */
    public static synchronized MongoDBManager getInstance() {
        if (instance == null) {
            instance = new MongoDBManager();
        }
        return instance;
    }
    
    /**
     * Get dashboard statistics
     * @return Document containing stats
     */
    public Document getStats() {
        Document stats = new Document();
        
        try {
            MongoCollection<Document> blockedCol = database.getCollection(BLOCKED_COLLECTION);
            MongoCollection<Document> queriesCol = database.getCollection(QUERIES_COLLECTION);
            
            // Total blocked domains
            long totalBlocked = blockedCol.countDocuments();
            
            // Blocked queries count
            long blockedQueries = queriesCol.countDocuments(Filters.eq("action", "blocked"));
            
            // Allowed queries count
            long allowedQueries = queriesCol.countDocuments(Filters.eq("action", "allowed"));
            
            stats.append("total_blocked_domains", totalBlocked)
                 .append("blocked_queries", blockedQueries)
                 .append("allowed_queries", allowedQueries)
                 .append("total_queries", blockedQueries + allowedQueries);
                 
        } catch (Exception e) {
            stats.append("total_blocked_domains", 0)
                 .append("blocked_queries", 0)
                 .append("allowed_queries", 0)
                 .append("total_queries", 0);
        }
        
        return stats;
    }
    
    /**
     * Get top blocked domains with counts
     * @param limit Maximum number of results
     * @return List of documents with domain and count
     */
    public List<Document> getTopBlocked(int limit) {
        List<Document> results = new ArrayList<>();
        
        try {
            MongoCollection<Document> queriesCol = database.getCollection(QUERIES_COLLECTION);
            
            AggregateIterable<Document> aggregate = queriesCol.aggregate(Arrays.asList(
                Aggregates.match(Filters.eq("action", "blocked")),
                Aggregates.group("$domain", Accumulators.sum("count", 1)),
                Aggregates.sort(Sorts.descending("count")),
                Aggregates.limit(limit),
                Aggregates.project(new Document("domain", "$_id").append("count", 1).append("_id", 0))
            ));
            
            for (Document doc : aggregate) {
                results.add(doc);
            }
        } catch (Exception e) {
            System.err.println("Error getting top blocked: " + e.getMessage());
        }
        
        return results;
    }
    
    /**
     * Get blocked query logs
     * @param limit Maximum number of results
     * @return List of blocked query documents
     */
    public List<Document> getBlockedLogs(int limit) {
        List<Document> results = new ArrayList<>();
        
        try {
            MongoCollection<Document> queriesCol = database.getCollection(QUERIES_COLLECTION);
            
            for (Document doc : queriesCol.find(Filters.eq("action", "blocked"))
                    .sort(Sorts.descending("_id"))
                    .limit(limit)) {
                // Remove MongoDB _id from response
                doc.remove("_id");
                results.add(doc);
            }
        } catch (Exception e) {
            System.err.println("Error getting blocked logs: " + e.getMessage());
        }
        
        return results;
    }
    
    /**
     * Get allowed query logs
     * @param limit Maximum number of results
     * @return List of allowed query documents
     */
    public List<Document> getAllowedLogs(int limit) {
        List<Document> results = new ArrayList<>();
        
        try {
            MongoCollection<Document> queriesCol = database.getCollection(QUERIES_COLLECTION);
            
            for (Document doc : queriesCol.find(Filters.eq("action", "allowed"))
                    .sort(Sorts.descending("_id"))
                    .limit(limit)) {
                doc.remove("_id");
                results.add(doc);
            }
        } catch (Exception e) {
            System.err.println("Error getting allowed logs: " + e.getMessage());
        }
        
        return results;
    }
    
    /**
     * Get all blocked domains
     * @param limit Maximum number of results
     * @return List of domain strings
     */
    public List<String> getAllDomains(int limit) {
        List<String> domains = new ArrayList<>();
        
        try {
            MongoCollection<Document> blockedCol = database.getCollection(BLOCKED_COLLECTION);
            
            for (Document doc : blockedCol.find()
                    .sort(Sorts.ascending("domain"))
                    .limit(limit)) {
                String domain = doc.getString("domain");
                if (domain != null) {
                    domains.add(domain);
                }
            }
        } catch (Exception e) {
            System.err.println("Error getting domains: " + e.getMessage());
        }
        
        return domains;
    }
    
    /**
     * Close database connection
     */
    public void close() {
        if (mongoClient != null) {
            mongoClient.close();
            System.out.println("MongoDB connection closed");
        }
    }
}
