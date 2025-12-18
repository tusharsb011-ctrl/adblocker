package com.dnsfilter.servlets;

import com.dnsfilter.db.MongoDBManager;
import org.bson.Document;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;

/**
 * Stats Servlet
 * GET /api/stats - Returns dashboard statistics
 */
@WebServlet("/api/stats")
public class StatsServlet extends HttpServlet {
    
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        // Set response type to JSON
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        
        // Enable CORS
        response.setHeader("Access-Control-Allow-Origin", "*");
        
        try {
            // Get stats from database
            MongoDBManager db = MongoDBManager.getInstance();
            Document stats = db.getStats();
            
            // Send JSON response
            PrintWriter out = response.getWriter();
            out.print(stats.toJson());
            out.flush();
            
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            PrintWriter out = response.getWriter();
            out.print("{\"error\": \"Failed to fetch statistics\"}");
        }
    }
}
