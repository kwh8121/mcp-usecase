from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider


public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAo4QNjJeDIFyqbMD5lIpn
rx2RZpxptEWS5hfzEqdijAJ2/TLhXyFDFCU6uMlKH7++7aJ3l7CLGE9Xu48o73qz
QDMw0bIzTrMbG8CDWd8Z7PRbCVVV8t6eCSPUKGkiuKk9m8gG2EJSt7yOaTfRmgFl
Ewbp8MC3PYeyz82DgI7JMkyr8qjSzrhC1+qE5Pj7SaFpI4LhTtgoTkz28MgdhZPn
JFl9Ig8en7ZF12YiYg/akH/YZTx6I12EMmAn1utRGd+Tn5m6jXBtCmIyXdLbX2k9
aYFoXCh760tCJhfXvORIBNrdtxqBu7nBNdTyGjlm+tt5T4GY5WAXDFRxdBSzQscR
aQIDAQAB
-----END PUBLIC KEY-----"""


auth = BearerAuthProvider(
    public_key=public_key,
    issuer="https://aidesk.koreatimes.co.kr",
    audience="calculator"
)


mcp = FastMCP(name="culcurator", auth=auth)


@mcp.tool()
def get_addition(a: int | float, b: int | float) -> int | float:
    """
    get_addition 툴은 두 수의 합을 반환합니다.

    Example:
        get_addition(1, 2) -> 3
        get_addition(1.5, 2.5) -> 4.0

     Args:
        a (int | float): 첫 번째 수
        b (int | float): 두 번째 수
    
    Returns:
        int | float: 두 수의 합
    """
    return a + b


@mcp.tool()
def get_subtraction(a: int | float, b: int | float) -> int | float:
    """
    get_subtraction 툴은 두 수의 차를 반환합니다.
    Example:
        get_subtraction(1, 2) -> -1
        get_subtraction(1.5, 2.5) -> -1.0

     Args:
        a (int | float): 첫 번째 수
        b (int | float): 두 번째 수
    
    Returns:
        int | float: 두 수의 차
    """
    return a - b    


@mcp.tool()
def get_multiplication(a: int | float, b: int | float) -> int | float:
    """
    get_multiplication 툴은 두 수의 곱을 반환합니다.

    Example:
        get_multiplication(1, 2) -> 2
        get_multiplication(1.5, 2.5) -> 3.75

     Args:
        a (int | float): 첫 번째 수
        b (int | float): 두 번째 수
    
    Returns:
        int | float: 두 수의 곱
    """
    return a * b


@mcp.tool()
def get_division(a: int | float, b: int | float) -> int | float:
    """
    get_division 툴은 두 수의 나눈 결과를 반환합니다.
    Example:
        get_division(1, 2) -> 0.5
        get_division(1.5, 2.5) -> 0.6

     Args:
        a (int | float): 첫 번째 수
        b (int | float): 두 번째 수
    
    Returns:
        int | float: 두 수의 나눈 결과
    """
    return a / b



# server.py 파일이 직접 실행될 때만 실행됩니다. 다른 모듈에서 임포트될 때는 실행되지 않습니다.
# host="0.0.0.0": 외부의 모든 IP 주소에서 원격 서버로 접근할 수 있도록 설정합니다.
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/",
        log_level="debug"
    )

