```shell
k create ns gateway-injection
k lable ns gateway-injection 

❯ istioctl tag set stable --revision 1-16
Revision tag "stable" created, referencing control plane revision "1-16". To enable injection using this
revision tag, use 'kubectl label namespace <NAMESPACE> istio.io/rev=stable'


❯ istioctl tag set canary --revision 1-16
Revision tag "canary" created, referencing control plane revision "1-16". To enable injection using this
revision tag, use 'kubectl label namespace <NAMESPACE> istio.io/rev=canary'
```

```
❯ istioctl manifest generate -o generated -f istio-operator-ingressgateway.yaml
Component dependencies tree:
Base
  Pilot

Rendering manifests to output dir generated
Rendering: Base
Writing manifest to generated/Base/Base.yaml
Rendering: Pilot
Writing manifest to generated/Base/Pilot/Pilot.yaml
Rendering: Cni
Writing manifest to generated/Base/Pilot/Cni/Cni.yaml
Rendering: IngressGateways
Writing manifest to generated/Base/Pilot/IngressGateways/IngressGateways.yaml
Rendering: EgressGateways
Writing manifest to generated/Base/Pilot/EgressGateways/EgressGateways.yaml

여기서 IngressGateways.yaml의 Deployment 복붙해서 istio-ingressgateway-canary-deployment.yaml 생성
istio: ingressgateway -> istio:ingressgateway-canary
istio.io/rev: 1-16 -> istio.io/rev: canary 
istio.io/rev: stable -> istio.io/rev: stable
이런 식으로 몇 개만 바꿔주면 됨

k create ns istio-ingress
namespace/istio-ingress created 

```

```
istioctl tag generate stable --revision 1-16 --overwrite | yq '[.webhooks[] | {"namespaceSelector": .namespaceSelector, "objectSelector": .objectSelector}]'
- namespaceSelector:
    matchExpressions:
      - key: istio.io/rev
        operator: In
        values:
          - stable
      - key: istio-injection
        operator: DoesNotExist
  objectSelector:
    matchExpressions:
      - key: sidecar.istio.io/inject
        operator: NotIn
        values:
          - "false"
- namespaceSelector:
    matchExpressions:
      - key: istio.io/rev
        operator: DoesNotExist
      - key: istio-injection
        operator: DoesNotExist
  objectSelector:
    matchExpressions:
      - key: sidecar.istio.io/inject
        operator: NotIn
        values:
          - "false"
      - key: istio.io/rev
        operator: In
        values:
          - stable
```

tag를 바탕으로한 mutating webhook이 저런 식임.
따라서 istio-ingress namespace에는 istio.io/rev=stable 이런 식으로 라벨을 달아두고 있다가

1. istioctl upgrade 후에 방금 업그레이드 한 revision을 istioctl tag set canary --revision 1-17
2. kubectl label ns istio-ingress istio.io/rev=canary
3. kubectl rollout restart -n istio-ingress deployment/istio-ingressgateway-canary
4. 후에 괜찮으면 1-17을 stable로 승격. istioctl tag set stable --revision 1-17
5. kubectl label ns istio-ingress istio.io/rev=stable
6. kubectl rollout restart -n istio-ingress deployment/isitio-ingressgateway

근데 단점이 gateway injection을 하더라도 istio 1-17을 설치하는 순간 일부 설정이 바뀌면서(?) istio.io/rev=stable인 ingressgateway가
동일하게 1-16을 바라보도록 설정되지만 재시작되어버림... 재시작이 될 지, 안 될 지는 사실 manifest로도 구분이 가능할 것 같긴함. .spec 아래에
변경사항이 있는가를 보면 될텐데. 일단 image tag가 변경되어버림;;; ㅋㅋㅋ;;;

image tag를 결과적으로는 mutating webhook이 넣어줄 수는 있지만, Deployment의 spec아래에 image tag 가 변경되면서 replicaset이 새로 생기고
그 replicaset으로 인해 생성되는 Pod의 image는 mutating webhook 덕에 새로운 태그 그대로가 아니라 이전 태그로 변경될 뿐임. 뭐 이미지 태그 뿐만 아니라
몇몇 revision dependent한 설정들 모두 이런 식임.

아무튼 그래서 gateway injection은 사용하지 않기로 했다.
