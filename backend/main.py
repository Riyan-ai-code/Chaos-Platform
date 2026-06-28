import asyncio
import datetime
import random
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Chaos Platform API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class Experiment(BaseModel):
    id: str
    name: str
    description: str
    type: str
    namespace: str
    target: str
    status: str
    lastRun: str

class ExperimentCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    type: str
    namespace: str
    target: str

class Result(BaseModel):
    runId: str
    name: str
    type: str
    status: str
    namespace: str
    target: str
    startedAt: str
    duration: str
    impact: str

class Settings(BaseModel):
    successRate: float
    simulationSpeed: int
    autoHeal: bool

# Helper to get formatted timestamps
def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# In-Memory Database State
DB_SETTINGS = {
    "successRate": 0.8,
    "simulationSpeed": 3,
    "autoHeal": True
}

DB_CLUSTER = {
    "status": "Healthy"
}

# Initial Experiments
DB_EXPERIMENTS = [
    {"id": "1", "name": "pod-kill-webapp", "description": "Kill Random Pods", "type": "Pod Kill", "namespace": "target-zone", "target": "web-app", "status": "Completed", "lastRun": "2025-06-26 10:30:15"},
    {"id": "2", "name": "network-latency", "description": "Inject Latency", "type": "Network Chaos", "namespace": "target-zone", "target": "payment-svc", "status": "Completed", "lastRun": "2025-06-26 10:29:42"},
    {"id": "3", "name": "cpu-stress-api", "description": "Stress CPU", "type": "CPU Stress", "namespace": "target-zone", "target": "api-service", "status": "Failed", "lastRun": "2025-06-26 10:10:31"},
    {"id": "4", "name": "memory-stress", "description": "Stress Memory", "type": "Memory Stress", "namespace": "target-zone", "target": "order-service", "status": "Completed", "lastRun": "2025-06-26 09:45:12"},
    {"id": "5", "name": "pod-delete", "description": "Delete Pods", "type": "Pod Delete", "namespace": "default", "target": "frontend", "status": "Completed", "lastRun": "2025-06-26 09:20:05"},
    {"id": "6", "name": "packet-loss-db", "description": "Inject Network Packet Loss", "type": "Network Chaos", "namespace": "target-zone", "target": "db-service", "status": "Idle", "lastRun": "Never"},
    {"id": "7", "name": "disk-fill-logs", "description": "Fill up ephemeral storage", "type": "Memory Stress", "namespace": "kube-system", "target": "fluentd", "status": "Idle", "lastRun": "Never"},
    {"id": "8", "name": "api-delay-gateway", "description": "Inject 500ms API gateway lag", "type": "Network Chaos", "namespace": "default", "target": "api-gateway", "status": "Idle", "lastRun": "Never"},
]

# Generate filler experiments to make it 24
for i in range(9, 25):
    DB_EXPERIMENTS.append({
        "id": str(i),
        "name": f"filler-experiment-{i}",
        "description": f"Simulated chaos exercise number {i}",
        "type": "Pod Kill" if i % 3 == 0 else "Network Chaos" if i % 3 == 1 else "CPU Stress",
        "namespace": "target-zone" if i % 2 == 0 else "default",
        "target": "auth-db" if i % 2 == 0 else "redis-cache",
        "status": "Idle",
        "lastRun": "Never",
    })

# Initial Results
DB_RESULTS = [
    {"runId": "r1", "name": "pod-kill-webapp", "type": "Pod Kill", "status": "Completed", "namespace": "target-zone", "target": "web-app", "startedAt": "2025-06-26 10:30:15", "duration": "2m 34s", "impact": "Low"},
    {"runId": "r2", "name": "network-latency", "type": "Network Chaos", "status": "Completed", "namespace": "target-zone", "target": "payment-svc", "startedAt": "2025-06-26 10:29:42", "duration": "5m 12s", "impact": "Medium"},
    {"runId": "r3", "name": "cpu-stress-api", "type": "CPU Stress", "status": "Failed", "namespace": "target-zone", "target": "api-service", "startedAt": "2025-06-26 10:10:31", "duration": "1m 08s", "impact": "High"},
    {"runId": "r4", "name": "memory-stress", "type": "Memory Stress", "status": "Completed", "namespace": "target-zone", "target": "order-service", "startedAt": "2025-06-26 09:45:12", "duration": "3m 45s", "impact": "Medium"},
    {"runId": "r5", "name": "pod-delete", "type": "Pod Delete", "status": "Completed", "namespace": "default", "target": "frontend", "startedAt": "2025-06-26 09:20:05", "duration": "1m 56s", "impact": "Low"},
    {"runId": "r6", "name": "network-latency", "type": "Network Chaos", "status": "Completed", "namespace": "target-zone", "target": "payment-svc", "startedAt": "2025-06-25 15:20:10", "duration": "5m 00s", "impact": "Low"},
    {"runId": "r7", "name": "pod-kill-webapp", "type": "Pod Kill", "status": "Failed", "namespace": "target-zone", "target": "web-app", "startedAt": "2025-06-25 14:15:33", "duration": "45s", "impact": "High"},
    {"runId": "r8", "name": "cpu-stress-api", "type": "CPU Stress", "status": "Completed", "namespace": "target-zone", "target": "api-service", "startedAt": "2025-06-25 11:05:00", "duration": "2m 10s", "impact": "Low"},
]

# Generate filler results to make it 48
types = ['Pod Kill', 'Network Chaos', 'CPU Stress', 'Memory Stress', 'Pod Delete']
impacts = ['Low', 'Medium', 'High']
statuses = ['Completed', 'Completed', 'Completed', 'Failed']

for i in range(9, 49):
    date = datetime.datetime.now() - datetime.timedelta(days=i // 3, hours=i % 24)
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    DB_RESULTS.append({
        "runId": f"r{i}",
        "name": "pod-kill-webapp" if i % 4 == 0 else "network-latency" if i % 4 == 1 else "cpu-stress-api" if i % 4 == 2 else "memory-stress",
        "type": types[i % len(types)],
        "status": statuses[i % len(statuses)],
        "namespace": "target-zone" if i % 3 == 0 else "default" if i % 3 == 1 else "kube-system",
        "target": "web-app" if i % 3 == 0 else "payment-svc" if i % 3 == 1 else "order-service",
        "startedAt": date_str,
        "duration": f"{random.randint(1, 5)}m {random.randint(10, 59)}s",
        "impact": impacts[i % len(impacts)],
    })

# Simulation Runner task
async def run_chaos_simulation(exp_id: str, run_id: str):
    # Load parameters
    speed = DB_SETTINGS["simulationSpeed"]
    rate = DB_SETTINGS["successRate"]
    auto_heal = DB_SETTINGS["autoHeal"]

    # 1. Wait duration
    await asyncio.sleep(speed)

    # 2. Determine outcome
    is_success = random.random() < rate
    final_status = "Completed" if is_success else "Failed"
    
    duration_min = random.randint(0, 1)
    duration_sec = random.randint(10, 59)
    duration_str = f"{f'{duration_min}m ' if duration_min > 0 else ''}{duration_sec}s"
    
    impact_opts = ["Low", "Medium"] if is_success else ["Medium", "High"]
    final_impact = random.choice(impact_opts)

    # 3. Update DB
    # Update Experiment status and last run
    for exp in DB_EXPERIMENTS:
        if exp["id"] == exp_id:
            exp["status"] = final_status
            exp["lastRun"] = get_current_timestamp()
            break
            
    # Update Result entry
    for res in DB_RESULTS:
        if res["runId"] == run_id:
            res["status"] = final_status
            res["duration"] = duration_str
            res["impact"] = final_impact
            break

    # 4. Handle cluster health impact
    if not is_success and not auto_heal:
        DB_CLUSTER["status"] = "Critical"
    elif not is_success and auto_heal:
        # Temporarily degrade then self-heal
        DB_CLUSTER["status"] = "Degraded"
        await asyncio.sleep(3)
        DB_CLUSTER["status"] = "Healthy"
    elif is_success and auto_heal:
        # Return to healthy if it was degraded
        DB_CLUSTER["status"] = "Healthy"

# API Endpoints
@app.get("/api/experiments", response_model=List[Experiment])
def get_experiments():
    return DB_EXPERIMENTS

@app.post("/api/experiments", response_model=Experiment)
def create_experiment(item: ExperimentCreate):
    new_exp = {
        "id": str(len(DB_EXPERIMENTS) + 1),
        "name": item.name,
        "description": item.description or f"Custom chaos targeting {item.target}",
        "type": item.type,
        "namespace": item.namespace,
        "target": item.target,
        "status": "Idle",
        "lastRun": "Never"
    }
    DB_EXPERIMENTS.insert(0, new_exp) # Add to top
    return new_exp

@app.post("/api/experiments/{id}/run", response_model=Result)
def run_experiment(id: str, background_tasks: BackgroundTasks):
    # Find experiment
    exp = next((e for e in DB_EXPERIMENTS if e["id"] == id), None)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Set state to Running
    exp["status"] = "Running"
    
    # Create running Result
    run_id = f"r_{int(datetime.datetime.now().timestamp())}"
    new_run = {
        "runId": run_id,
        "name": exp["name"],
        "type": exp["type"],
        "status": "Running",
        "namespace": exp["namespace"],
        "target": exp["target"],
        "startedAt": get_current_timestamp(),
        "duration": "--",
        "impact": "Pending"
    }
    DB_RESULTS.insert(0, new_run) # Add to top

    # Temporarily degrade cluster health on stress runs
    if DB_CLUSTER["status"] == "Healthy" and exp["type"] in ["CPU Stress", "Memory Stress"]:
        DB_CLUSTER["status"] = "Degraded"

    # Queue background simulator task
    background_tasks.add_task(run_chaos_simulation, id, run_id)
    
    return new_run

@app.get("/api/results", response_model=List[Result])
def get_results():
    return DB_RESULTS

@app.get("/api/cluster/health")
def get_cluster_health():
    return {"status": DB_CLUSTER["status"]}

@app.post("/api/cluster/health/{status}")
def override_cluster_health(status: str):
    if status not in ["Healthy", "Degraded", "Critical"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    DB_CLUSTER["status"] = status
    return {"status": DB_CLUSTER["status"]}

@app.get("/api/settings", response_model=Settings)
def get_settings():
    return DB_SETTINGS

@app.post("/api/settings", response_model=Settings)
def update_settings(item: Settings):
    DB_SETTINGS["successRate"] = item.successRate
    DB_SETTINGS["simulationSpeed"] = item.simulationSpeed
    DB_SETTINGS["autoHeal"] = item.autoHeal
    return DB_SETTINGS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
