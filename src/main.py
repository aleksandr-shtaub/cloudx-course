from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import httpx


IMDS_URL = "http://169.254.169.254/latest"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(base_url=IMDS_URL, timeout=2) as client:
        headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        res_token = await client.put("/api/token", headers=headers)
        token = res_token.text

        headers = {"X-aws-ec2-metadata-token": token}
        res_region = await client.get("/meta-data/placement/region", headers=headers)
        res_az = await client.get("/meta-data/placement/availability-zone", headers=headers)

        yield {
            "client": client,
            "meta": {
                "region": res_region.text,
                "availability-zone": res_az.text
            }
        }


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root(request: Request):
    return request.state.meta
