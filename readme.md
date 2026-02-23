# lệnh docker để run image qdrant
``` bash
 (Chạy ở powershell)

docker run -p 6333:6333 -p 6334:6334 `
    -v ${PWD}/qdrant_storage:/qdrant/storage:z `
    qdrant/qdrant
```
link localhost
```
http://localhost:6333/dashboard
```