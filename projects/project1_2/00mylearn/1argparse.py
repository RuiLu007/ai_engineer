# 导入必要的类型注解（新手可先忽略，仅用于说明类型）
from typing import Any, ClassVar

# 基础父类（简化示意，实际在 Python 内置/第三方库中）
class _AttributeHolder:
    pass

# 核心的 Namespace 类
class Namespace(_AttributeHolder):
    # 1. 构造方法：初始化对象时接收任意关键字参数
    def __init__(self, **kwargs: Any) -> None:
        # 把传入的所有关键字参数（比如 name="张三", age=18）变成对象属性
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    # 2. 自定义“获取不存在的属性”的逻辑
    def __getattr__(self, name: str) -> Any:
        # 当访问 obj.xxx 但 xxx 不存在时，会触发这个方法
        raise AttributeError(f"'Namespace' object has no attribute '{name}'")

    # 3. 自定义“设置属性”的逻辑
    def __setattr__(self, name: str, value: Any, /) -> None:
        # 当执行 obj.xxx = 123 时，会触发这个方法
        # / 表示前面的参数是位置参数，不能用关键字传参（新手暂时忽略这个细节）
        super().__setattr__(name, value)  # 调用父类的设置属性方法

    # 4. 支持 "xxx in obj" 这样的判断
    def __contains__(self, key: str) -> bool:
        # 比如判断 'name' 是否在 Namespace 对象中：'name' in obj
        return hasattr(self, key)

    # 5. 支持两个 Namespace 对象用 == 比较
    def __eq__(self, other: object) -> bool:
        # 只有当 other 是 Namespace 实例，且所有属性都相等时，返回 True
        if not isinstance(other, Namespace):
            return False
        # 把对象的属性转成字典，比较字典是否相等
        return self.__dict__ == other.__dict__

    # 6. 禁用哈希（表示该对象不能作为字典的键/集合的元素）
    __hash__: ClassVar[None] = None

ns = Namespace(name="张三", age=20)
print(ns.name)  # 输出：张三
print(ns.age)   # 输出：20

ns = Namespace(name="张三")
print(ns.gender)  # 触发 __getattr__，抛出 AttributeError: 'Namespace' object has no attribute 'gender'

ns = Namespace(name="张三")
ns.gender = "男"  # 触发 __setattr__，给对象新增 gender 属性
print(ns.gender)  # 输出：男

ns = Namespace(name="张三")
print('name' in ns)   # 输出：True
print('gender' in ns) # 输出：False
