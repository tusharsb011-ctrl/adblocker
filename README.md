# DNS Filter Dashboard

A full-stack DNS filtering system built with **MongoDB**, **Java (JSP, Servlets, JavaBeans)**, and **Node.js**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DNS Filter System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │   Node.js API    │    │   Java Servlets  │               │
│  │   (Express.js)   │    │   (Tomcat/Jetty) │               │
│  │   Port: 8000     │    │   Port: 8080     │               │
│  └────────┬─────────┘    └────────┬─────────┘               │
│           │                       │                          │
│           └───────────┬───────────┘                          │
│                       │                                      │
│               ┌───────▼───────┐                              │
│               │    MongoDB    │                              │
│               │  dns_filter   │                              │
│               └───────────────┘                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technologies Used

### Backend
- **Node.js** with Express.js - RESTful API server
- **Java Servlets** - Alternative Java-based API
- **JavaBeans** - Data model classes
- **JSP (Java Server Pages)** - Server-side rendering

### Database
- **MongoDB** - NoSQL database for storing queries and blocked domains

### Frontend
- **HTML/CSS/JavaScript** - Dashboard interface
- **JSP** - Java-based dynamic pages

## 📁 Project Structure

```
dns-filter/
├── server.js                 # Node.js Express server
├── package.json              # Node.js dependencies
├── .env                      # Environment configuration
├── dashboard.html            # Static HTML dashboard
├── blocklist.txt             # Blocked domains list
│
├── db/
│   └── mongodb.js            # MongoDB connection and models
│
├── routes/
│   └── api.js                # RESTful API routes
│
├── scripts/
│   └── init-mongodb.js       # Database initialization
│
└── dns-filter-jsp/           # Java Web Application
    ├── pom.xml               # Maven configuration
    ├── src/
    │   └── com/dnsfilter/
    │       ├── beans/        # JavaBeans
    │       │   ├── QueryBean.java
    │       │   ├── BlockedDomainBean.java
    │       │   └── StatsBean.java
    │       ├── dao/          # Data Access Objects
    │       │   └── MongoDBDAO.java
    │       ├── servlets/     # Servlets
    │       │   ├── DashboardServlet.java
    │       │   ├── StatsServlet.java
    │       │   ├── DomainsServlet.java
    │       │   └── LogsServlet.java
    │       └── filters/      # Servlet Filters
    │           ├── CorsFilter.java
    │           └── CharacterEncodingFilter.java
    └── webapp/
        ├── index.jsp         # Welcome page
        └── WEB-INF/
            ├── web.xml       # Servlet configuration
            └── jsp/
                ├── dashboard.jsp
                └── error.jsp
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v14 or higher)
- **MongoDB** (v4.4 or higher)
- **Java JDK** (v11 or higher)
- **Apache Tomcat** (v9 or higher) or **Jetty**
- **Maven** (for Java build)

### Installation

#### 1. Clone the repository
```bash
cd "with webtech - Copy"
```

#### 2. Install Node.js dependencies
```bash
npm install
```

#### 3. Start MongoDB
```bash
# Windows
mongod

# Or start MongoDB service
net start MongoDB
```

#### 4. Initialize the database
```bash
npm run init-db
```

#### 5. Start the Node.js server
```bash
npm start
```

The dashboard will be available at: `http://localhost:8000`

### Running the Java Application

#### Using Maven
```bash
cd dns-filter-jsp

# Build the WAR file
mvn clean package

# Run with embedded Tomcat
mvn tomcat7:run

# Or run with Jetty
mvn jetty:run
```

The Java dashboard will be available at: `http://localhost:8080/dns-filter`

## 📡 API Endpoints

### Node.js API (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Get dashboard statistics |
| GET | `/api/top-blocked` | Get top blocked domains |
| GET | `/api/logs/blocked` | Get blocked query logs |
| GET | `/api/logs/allowed` | Get allowed query logs |
| GET | `/api/logs/recent` | Get recent activity |
| GET | `/api/domains` | Get all blocked domains |
| POST | `/api/domains` | Add a blocked domain |
| DELETE | `/api/domains/:domain` | Remove a blocked domain |
| GET | `/api/check/:domain` | Check if domain is blocked |
| POST | `/api/log` | Log a DNS query |

### Java Servlet API (Port 8080)

Same endpoints are available under `/dns-filter/api/*`

## 📊 Database Schema

### Collections

#### `queries`
```javascript
{
  _id: ObjectId,
  clientIp: String,
  domain: String,
  queryType: String,      // "A", "AAAA", etc.
  action: String,         // "allowed" or "blocked"
  responseTime: Number,   // in milliseconds
  timestamp: Date
}
```

#### `blockeddomains`
```javascript
{
  _id: ObjectId,
  domain: String,         // unique
  category: String,       // "ads", "tracking", "malware", etc.
  addedAt: Date,
  addedBy: String
}
```

## 🎨 Features

- ✅ Real-time DNS query logging
- ✅ Domain blocking/unblocking
- ✅ Statistics dashboard
- ✅ Top blocked domains chart
- ✅ Query history (blocked/allowed)
- ✅ Category-based blocking
- ✅ RESTful API
- ✅ CORS support
- ✅ Dual backend (Node.js + Java)

## 🔧 Configuration

### Environment Variables (.env)
```
MONGODB_URI=mongodb://localhost:27017/dns_filter
PORT=8000
```

### Java Configuration (web.xml)
```xml
<context-param>
    <param-name>mongodbUri</param-name>
    <param-value>mongodb://localhost:27017/dns_filter</param-value>
</context-param>
```

## 📝 License

MIT License

## 👥 Contributors

- DNS Filter Team
