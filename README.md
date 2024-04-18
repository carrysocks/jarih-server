## 자리있어 API 서버

사용자가 노선, 정류장, 즐겨찾기 정보들을 확인하는 기능을 처리하는 API 서버입니다.

---
## 목차

- [설치](#설치)
- [사용법](#사용법)
- [성능 비교](#성능-비교)


---
### 설치


요구사항 : Python 3.9


1. **레포지토리 클론**

```bash
git clone https://github.com/carrysocks/jarih-server.git
cd jarih-server
```

2. **가상 환경 설정**

```bash
virtualenv venv
source venv/bin/activate 
```

3. **의존성 설치**

```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**

.env 에는 DB_URL, SECRET_KEY, ALGORITHM, LAMBDA_ENDPOINT 가 담겨야합니다.

```bash
source .env
```


### 사용법

uvicorn 환경에서 Fastapi 서버가 돌아갑니다.

```bash
python run.py
```

----




