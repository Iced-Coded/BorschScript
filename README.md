<p align="center">
  <img src="img/icon.png" alt="BorschScript Logo" width="150" /><br />
  <sub
    ><a
      href="https://www.flaticon.com/free-icons/russian-food"
      title="russian food icons"
      >Russian food icons created by Muhammad_Usman - Flaticon</a
    ></sub
  >
</p>
<h1 align="center">BorschScript</h1>

<p align="center">
  <b>BorschScript</b>, an esoteric, XML-like programming language written in Ukrainian.
</p>

---

## Installation

### From pypi

Install it using `pip`:

```bash
pip install borschscript
```

### From GitHub Releases

1. Go to the [Releases](https://github.com/Iced-Coded/borshscript/releases) page.
2. Download the latest `.whl` package (or the standalone executable for your OS).
3. If using the `.whl` package, install it using `pip`:

```bash
pip install borschscript-[version]-py3-none-any.whl
```

### From Source
Clone the repository and install it locally using `pip`:

```bash
git clone [https://github.com/your-username/borshscript.git](https://github.com/your-username/borshscript.git)
cd borshscript
pip install -e .
```

## Quick Start

Create a script file named `recipe.brsh`:

```xml
<змінна назва="порції">3</змінна>

<функція назва="зварити_борщ" аргументи="кількість">
    <друк>f"Варимо борщ на {кількість} порції!"</друк>
</функція>

<якщо умова="порції >= 3">
    <викликати назва="зварити_борщ" аргументи="порції" />
</якщо>
<інакше>
    <друк>"Занадто мало інгредієнтів..."</друк>
</інакше>
```

Run your script from the terminal:

```bash
borsch recipe.brsh
```

### Debug Mode

To inspect the transpiled Python code before execution, pass the --debug flag:

```bash
borsch recipe.brsh --debug
```

## Language Syntax Overview

|BorschScript|Description|Python Equivalent|
|-|-|-|
|`<змінна назва="X">значення</змінна>`|Declare variable|`X = значення`|
|`<друк>значення</друк>`|Print output|`print(значення)`|
|`<якщо умова="X">`|Conditional statement|if X:|
|`<інакше>`|Else block|`else:`|
|`<поки умова="X">`|While loop|`while X:`|
|`<функція назва="X" аргументи="A, B">`|Define function|`def X(A,B)`|
|`<повернути>значення</повернути>`|Return statement|`return значення`|
|`<викликати назва="X" аргументи="A" />`|Call function|`X(A)`|

## License

Distributed under **BSD-3** License. See [LICENSE](LICENSE) for more info.