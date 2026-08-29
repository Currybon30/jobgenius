from app.services.job_service import mcp as job_service_mcp

if __name__ == "__main__":
    job_service_mcp.run(transport="stdio")