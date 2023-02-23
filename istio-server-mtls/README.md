```shell
kubectl view-secret -n istio-system server-tls ca.crt > certificates/server/ca.crt
kubectl view-secret -n istio-system server-tls tls.crt > certificates/server/tls.crt
kubectl view-secret -n istio-system server-tls tls.key > certificates/server/tls.key
kubectl view-secret jinsu-tls ca.crt > certificates/jinsu/ca.crt
kubectl view-secret jinsu-tls tls.crt > certificates/jinsu/tls.crt
kubectl view-secret jinsu-tls tls.key > certificates/jinsu/tls.key
```

k8s 리소스들 배포 후 Cert Manager가 생성해준 인증서들을 로컬에 저장한다 ㅎㅅㅎ
이때 Cert manager가 생성한 self-signed-ca가 istio ingressgateway와 내 클라이언트 인증서의 부모이다.

```shell
openssl pkcs12 -export -inkey certificates/jinsu/tls.key -in certificates/jinsu/tls.crt -out jinsu.p12
```

중요: 브라우저들은 `.p12` 파일을 받는 듯함! tls.crt만 전달해서는 안된다. 당연히 tls.key도 전달할 수 있어야하는데 이 기법이
pkcs12인 것이다.
OSX 기준 Keychain Access의 Sidebar에서 login 부분에 넣든
System 부분에 넣든 별 상관 없음. Certificates 항목으로 추가하기만 하면.
