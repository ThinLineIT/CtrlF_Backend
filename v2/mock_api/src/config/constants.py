MOCK_REFRESH_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIxMjMxMjMiLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9"
    ".DXi8E6qG8SI4Xzwur1JDsjmVtujkcV3cOF2_LIBjkHI"
)  # noqa: E501
MOCK_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # noqa: E501


PAGE_CONTENT_1 = """
# 서로소 집합 알고리즘 (Disjoint Sets)
- 서로소 집합의 정의
- 서로소 집합 자료구조
- 서로소 집합 알고리즘 소스코드 (Python)
- 서로소 집합을 활용한 사이클 판별
- 서로소 집합을 활용한 사이클 판별 소스코드 (Python)


## You can answer
- 서로소 집합이 무엇인가?
- 서로소 집합 자료구조는 무엇인가?
- 서로소 집합을 활용한 사이클 판별의 소스코드를 작성해보아라.
-----------------------

## 서로소 집합의 정의
- 수학에서 서로소 집합이란 공통 원소가 없는 두 집합을 의미한다. 예를 들어 집합 {1,2}와 집합{3,4}는 서로소 관계이다. 반면에 집합{1,2}와 집합{2,3}은 2라는 원소가 두 집합에 공통적으로
포함되어 있기 때문에 서로소 관계가 아니다.
서로소 집합 자료구조란 **서로소 부분 집합들로 나누어진 원소들의 데이터를 처리하기 위한 자료구조**라고 할 수 있다. 서로소 집합 자료구조는 union과 find 이 2개의 연산으로 조작할 수 있다.
서로소 집합 자료구조는 union-find(합치기 찾기) 자료구조라고 불리기도 한다.

- union(합집합) 연산: 2개의 원소가 포함된 집합을 하나의 집합으로 합치는 연산.
- find(찾기) 연산: 특정한 원소가 속한 집합이 어떤 집합인지 알려주는 연산.

</br>

## 서로소 집합 자료구조
- 서로소 집합 자료구조를 구현할 때는 **트리 자료구조**를 이용하여 집합을 표현한다.

- 서로소 집합 계산 알고리즘</br>
1.union(합집합) 연산을 확인하여, 서로 연결된 두 노드 A,B를 확인한다.</br>
ⅰ. A와 B의 루트 노드 A',B'를 각각 찾는다.</br>
ⅱ. A'를 B'의 부모 노드로 설정한다 (B'가 A'를 가리키도록 한다 = 부모 노드로 설정한다)</br>
2.모든 union(합집합) 연산을 처리할 때까지 1번 과정을 반복한다.

- union 연산들은 그래프 형태로 표현될 수도 있다. 각 원소는 그래프에서의 노드로 표현되고, '같은 집합에 속한다'는 정보를 담은 union 연산들은 간선으로 표현된다.
다른 두 원소에 대해 union을 수행해야 할 때는 각각 루트 노드를 찾아서 더 큰 루트 노드가 더 작은 루트 노드를 가리키도록 하면 된다.

</br>

## 서로소 집합 알고리즘 소스코드 (Python)
```Python
#서로소 집합 알고리즘 소스코드
def find_parent(parent,x):
    if parent[x]!=x:
        parent[x]=find_parent(parent,parent[x])

    return parent[x]
#두 원소가 속한 집합을 합치기
def union_parent(parent,a,b):
    a=find_parent(parent,a)
    b=find_parent(parent,b)
    if a<b:
        parent[b]=a
    else:
        parent[a]=b

#노드의 개수와 간선(union 연산)의 개수 입력받기
v,e=map(int,input().split())
parent=[0]*(v+1) #부모 테이블 초기화
#부모 테이블상에서, 부모를 자기 자신으로 초기화
for i in range(1,v+1):
    parent[i]=i
#union 연산을 각각 수행
for _ in range(e):
    a,b = map(int,input().split())
    union_parent(parent,a,b)
#각 원소가 속한 집합 출력
print('각 원소가 속한 집합: ',end='')
for i in range(1,v+1):
    print(find_parent(parent,i),end=' ')
print()
#부모 테이블 내용 출력
print('부모 테이블: ',end='')
for i in range(1,v+1):
    print(parent[i],end=' ')
```
- 서로소 집합 알고리즘 실행 과정
![DisjointSets_1](./img/DisjointSets_1.png)

- 이 알고리즘에서 유의할 점은 union 연산을 효과적으로 수행하기 위해 '부모 테이블'을 항상 가지고 있어야 한다는 점이다. 또한 루트 노드를 즉시 계산할 수 없고, 부모 테이블을 계속해서 확인하며 거슬러 올라가야 한다.

<br/>

## 서로소 집합을 활용한 사이클 판별
- 서로소 집합은 다양한 알고리즘에 사용될 수 있다. 특히 서로소 집합은 무방향 그래프 내에서의 사이클을 판별할 때 사용할 수 있다는 특징이 있다. 방향 그래프에서의 사이클 여부는 DFS를 이용하여 판별할 수 있다.

</br>

## 서로소 집합을 활용한 사이클 판별 소스코드 (Python)

- 이 알고리즘은 간선에 방향성이 없는 무방향 그래프에서만 적용 가능하다.
```
# 서로소 집합 알고리즘 소스코드
def find_parent(parent,x):
    if parent[x]!=x:
        parent[x]=find_parent(parent,parent[x])
    return parent[x]
def union_parent(parent,a,b):
    a = find_parent(parent,a)
    b = find_parent(parent,b)
    if a<b:
        parent[b]=a
    else:
        parent[a]=b
v,e = map(int,input().split())
parent = [0]*(v+1)
for i in range(1,v+1):
    parent[i]=i
cycle = False
for _ in range(e):
    a,b=map(int,input().split())

    if find_parent(parent,a)==find_parent(parent,b):
        cycle = True
        break
    else:
        union_parent(parent,a,b)

if cycle:
    print("사이클이 발생했습니다.")
else:
    print("사이클이 발생하지 않았습니다.")

```

<br/>

## Reference
- 이것이 취업을 위한 코딩 테스트다 with 파이썬 (나동빈 저자)
- [서로소 집합 알고리즘 실행 과정 이미지 출처](https://travelbeeee.tistory.com/369)
"""

PAGE_CONTENT_2 = """
# 동적 계획법(Dynamic Programming)

- 동적계획법이란?
- 특징
- 장단점
- 분할 정복(Divide and Conquer)과의 차이점
- 종류
- 구현

## You Can Answer
- 동적계획법이란 무엇인가요?
- 동적계획법의 특징에 대해 설명해보세요.
- 분할 정복(Divide and Conquer)과 다른 점이 무엇인가요?
-----------------------

## 동적계획법이란?
큰 문제를 작은 문제로 나누어 작은 부분 문제들을 해결한 것을 가지고 큰 부분 문제들을 해결하여 최종적으로 전체 문제를 해결하는 알고리즘


## 특징
- 상향식 접근법
가장 작은 문제들로부터 답을 구해가며 전체 문제의 답을 찾는 방식
- Memoization 기법 사용
  - Memoization이란?
  동일한 계산을 반복할 때 이전에 계산한 값을 메모리에 저장함으로써 동일한 계산의 반복 수행을 제거하는 기술
- 부분 문제 중복

## 장단점
- 장점
  - 프로그램을 구현할 때 필요한 모든 가능성을 고려하여 항상 최적의 결과를 얻을 수 있다.
  - 메모리에 저장된 값을 사용하므로 빠른 속도로 문제를 해결할 수 있다.
- 단점
  - 모든 가능성에 대한 고려가 불충분할 경우 최적의 결과를 보장할 수 없다.
  - 다른 방법론에 비해 많은 메모리 공간을 요구한다.

## 분할 정복(Divide and Conquer)과의 차이점
큰 문제를 작은 문제로 나누는 부분에 있어서는 공통점이 있지만 다이나믹 프로그래밍은 작은 문제(동일한 계산)가 반복적으로 나타나고 분할정복은 반복이 일어나지 않는다.

## 종류
- 탑다운(Top-Down) 방식
  - 큰 문제를 해결하기 위해 작은 문제를 호출하는 방식으로 '하향식'이라고도 한다.
- 바텀업(Bottom-Up) 방식
  - 가장 작은 문제들부터 답을 구해가며 전체 문제의 답을 찾는 방식으로 '상향식'이라고도 한다.

## 구현(파이썬)
### 탑다운 방식
```python
# 메모이제이션하기 위한 리스트 초기화
memoization = [0] * 100


# 피보나치 함수를 재귀함수로 구현 (Top-down DP)
def fibo(x):
    if x == 1 or x == 2:
        return 1
    # 이미 계산한 적 있으면 그대로 반환
    if memoization[x] != 0:
        return memoization[x]
    # 계산한 적 없으면 점화식에 따라 피보나치 결과 반환
    memoization[x] = fibo(x - 1) + fibo(x - 2)
    return memoization[x]


print(fibo(6))
```
fibo(6)을 구하는 과정은 아래 그림과 같다.
![DP_image](./img/DP_image.png)
메모이제이션을 사용하여 색칠된 노드만 방문하게 된다.

### 바텀업 방식
```python
dp = [0] * 100
dp[1] = 1
dp[2] = 1
n = 99

# 피보나치 수열 반복문으로 구현(Bottom-Up DP)
for i in range(3, n + 1):
    dp[i] = dp[i - 1] + dp[i - 2]

print(dp[n])
```
---
## Reference
- [다이나믹 프로그래밍(Dynamic Programming)](https://velog.io/@kimdukbae/%EB%8B%A4%EC%9D%B4%EB%82%98%EB%AF%B9-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-Dynamic-Programming)
- [알고리즘 - Dynammic Programming(동적프로그래밍)이란?](https://galid1.tistory.com/507)

"""

PAGE_CONTENT_3 = """
# Prim's algorithm
- Definition
  - what is prim's algorithm?
- Prim's algorithm의 동작과 예시
  - 동작
  - 예시
- Prim's algorithm의 시간복잡도
  - 시간복잡도

## You can answer
- 프림의 알고리즘의 동작과정을 설명할 수 있는가?
- 프림의 알고리즘의 시간복잡도를 구할 수 있는가?
---


## Definition
### What is prim's algorithm?
```
Greedy Approach의 일종으로 출발점으로부터 거리가 가장 짧은 점들을 따라 이동하며 최종적으로 모든점을 경유하는 알고리즘이다.
```


## Prim's algorithm의 동작과 예
### 동작
```
1. 하나의 정점으로부터 시작된다
2. 정점으로부터의 가중치가 가장 낮은 간선을 찾아 간선이 잇는 점을 연결한다
3. 시작점을 포함해 연결된 모든 점들중(이미 연결된 점들은 제외) 가중치가 가장 낮은 간선을 찾아 새로운 점과 연결한다
4. 위 과정을 반복해 모든 점들을 연결한다
```
### 예시
![Prim](https://user-images.githubusercontent.com/70050038/116186329-5a60f480-a75e-11eb-9a6a-9f2cd7dbd657.PNG)
- Graph (V, F)로 부터 MST를 찾는 과정
1. 임의의 정점(node)을 정한다 (V1) (두번째 그래프 참조)
   - V = { V&#8321; }, F = Ø
2. 정점에서 가장 가중치가 낮은 간선(egde)을 연결한다 (세번째 그래프 참조)
   - V = { V&#8321;, V&#8322; }, F = { (V&#8321; - V&#8322;) }
3. set V 에서 연결할 수 있는 가중치가 가장 낮은 간선(egde)을 연결한다. (세번 째 그래프 참조)
   - 이 경우 (V₁ - V&#8323;), (V&#8322; - V&#8323;), (V&#8322; - V&#8324;) 중 한개를 선택 할 수 있는데, 가장 짧은 간선 중 하나인 (V₁ - V&#8323;) 선택
   - V = { V&#8321;, V&#8322;, V&#8323; }, F = { (V&#8321; - V&#8322;), (V&#8321; - V&#8323;) }
4. 이후의 과정도 위와 같은 방식으로 set V의 요소들 중 연결할 수 있는 가장 작은 간선을 연결하여 MST에 도달한다 (여섯 째 그래프 참조)
   - V = { V&#8321;, V&#8322;, V&#8323;, V&#8324;, V&#8325; }, F = { (V&#8321; - V&#8322;), (V&#8321; - V&#8323;), (V&#8323; - V&#8324;), (V&#8323; - V&#8325;) }


## Prim's algorithm의 시간복잡도
### 시간복잡도
- 정점(node)의 수 (n - 1) (초기 정점 V&#8321; 제외), 정점 당 연결 될 수 있는 간선의 수 (n - 1)만큼 반복
- 시간 복잡도 : (n - 1) * (n - 1) ∈ O(n&#178;)
"""


PAGE_CONTENT_4 = """
# 선택 정렬(selection sort)
<!--Table of Contents-->
- 선택정렬 이란?
  - 정의
  - 복잡도
- 구현



<!-- 어떤 질문을 대답할 수 있어야 하는지-->
## You can answer
- 선택정렬이란 무엇인가요 ?
- 선택정렬은 어떻게 구현할 수 있나요 ?

<!--Contents-->

---
## 선택 정렬(selection sort) 란?
* 기본 정렬 알고리즘 중 하나로 다음과 같은 순서를 반복하며 정렬하는 알고리즘
    1) 주어진 데이터 중 최소값을 찾는다
    2) 해당 최소값을 데이터 맨 앞에 위치한 값과 바꾼다
    3) 그 다음 데이터도 같은 방식으로 최소값과 교체한다.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![selection_sort_gif](https://upload.wikimedia.org/wikipedia/commons/9/94/Selection-Sort-Animation.gif)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
By <a href="https://en.wikipedia.org/wiki/User:Joestape89" class="extiw" title="en:User:Joestape89">Joestape89</a>, <a href="http://creativecommons.org/licenses/by-sa/3.0/" title="Creative Commons Attribution-Share Alike 3.0">CC BY-SA 3.0</a>, <a href="https://commons.wikimedia.org/w/index.php?curid=3330231">Link</a>

* 시간 복잡도
  + 두 개의 for 루프의 실행 횟수
    + 외부 루프 :  (n-1) 번
    + 내부 루프 : n-1, n-2, ... , 2, 1 번
  + 교환 횟수 = 외부 루프의 실행 횟수 (즉, 상수 시간 작업)

 ![수식](https://latex.codecogs.com/gif.latex?%7B%5Cdisplaystyle%20C_%7Bmin%7D%3DC_%7Bave%7D%3DC_%7Bmax%7D%3D%5Csum%20_%7Bi%3D1%7D%5E%7BN-1%7D%7BN-i%7D%3D%7B%5Cfrac%20%7BN%28N-1%29%7D%7B2%7D%7D%3DO%28n%5E%7B2%7D%29%7D)

## 구현
### 데이터가 두 개 일 때,
    예 ) data_list = [5,1]
        data_list[0] > data_list[1] 이므로 값 서로 교환

### 데이터가 네 개 일 때,
    예 ) data_list = [8,6,5,1]
        첫 번째 실행 -> [1,6,5,8]
        두 번째 실행 -> [1,5,6,8]
        세 번째 실행 -> 변화 없음
### 구현 (파이썬)
```python
def selection_sort(data):
  for stand in range(len(data) - 1):
      lowest = stand
      for index in range(stand + 1, len(data)):
          if data[lowest] > data[index]:
              lowest = index
      data[lowest], data[stand] = data[stand], data[lowest]
  return data
```
### 구현 (C 언어)
```c
void selectionSort(int *list, const int n)
{
  int i, j, indexMin, temp;

  for (i = 0; i < n - 1; i++)
  {
      indexMin = i;
      for (j = i + 1; j < n; j++)
      {
          if (list[j] < list[indexMin])
          {
              indexMin = j;
          }
      }
      temp = list[indexMin];
      list[indexMin] = list[i];
      list[i] = temp;
    }
}
```
## 구현 (JAVA)
```java
void selectionSort(int[] list) {
  int indexMin, temp;

  for (int i = 0; i < list.length - 1; i++) {
      indexMin = i;
      for (int j = i + 1; j < list.length; j++) {
          if (list[j] < list[indexMin]) {
              indexMin = j;
          }
      }
      temp = list[indexMin];
      list[indexMin] = list[i];
      list[i] = temp;
  }
}
```
---
## Reference
- [Selection sort](https://en.wikipedia.org/wiki/Selection_sort)
- [선택 정렬](https://ko.wikipedia.org/wiki/%EC%84%A0%ED%83%9D_%EC%A0%95%EB%A0%AC)

"""
