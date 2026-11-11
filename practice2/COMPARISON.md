# Сравнение с dotnet restore

## Newtonsoft.Json 13.0.3

### Независимый DFS порядок

Newtonsoft.Json/13.0.3

### Штатный граф NuGet из project.assets.json

- Microsoft.NETCore.Platforms/1.1.0 → нет зависимостей
- NETStandard.Library/2.0.3 → {'Microsoft.NETCore.Platforms': '1.1.0'}
- Newtonsoft.Json/13.0.3 → нет зависимостей

### Сопоставление

NuGet объединяет ограничения версий и учитывает приоритет прямых зависимостей. Учебный DFS хранит узлы как пары имя и версия и выбирает минимальную версию отдельно для каждого ребра. Поэтому могут появиться две версии одного пакета. Также штатный restore добавляет NETStandard.Library для целевой платформы, а учебный граф начинается с пакета.

## Serilog 3.1.1

### Независимый DFS порядок

System.Buffers/4.5.1 → System.Numerics.Vectors/4.4.0 → System.Runtime.CompilerServices.Unsafe/4.5.3 → System.Memory/4.5.5 → System.Runtime.CompilerServices.Unsafe/6.0.0 → System.Diagnostics.DiagnosticSource/7.0.2 → Serilog/3.1.1

### Штатный граф NuGet из project.assets.json

- Microsoft.NETCore.Platforms/1.1.0 → нет зависимостей
- NETStandard.Library/2.0.3 → {'Microsoft.NETCore.Platforms': '1.1.0'}
- Serilog/3.1.1 → {'System.Diagnostics.DiagnosticSource': '7.0.2'}
- System.Buffers/4.5.1 → нет зависимостей
- System.Diagnostics.DiagnosticSource/7.0.2 → {'System.Memory': '4.5.5', 'System.Runtime.CompilerServices.Unsafe': '6.0.0'}
- System.Memory/4.5.5 → {'System.Buffers': '4.5.1', 'System.Numerics.Vectors': '4.4.0', 'System.Runtime.CompilerServices.Unsafe': '4.5.3'}
- System.Numerics.Vectors/4.4.0 → нет зависимостей
- System.Runtime.CompilerServices.Unsafe/6.0.0 → нет зависимостей

### Сопоставление

NuGet объединяет ограничения версий и учитывает приоритет прямых зависимостей. Учебный DFS хранит узлы как пары имя и версия и выбирает минимальную версию отдельно для каждого ребра. Поэтому могут появиться две версии одного пакета. Также штатный restore добавляет NETStandard.Library для целевой платформы, а учебный граф начинается с пакета.

## Microsoft.Extensions.Logging.Abstractions 8.0.0

### Независимый DFS порядок

System.Runtime.CompilerServices.Unsafe/4.5.3 → System.Threading.Tasks.Extensions/4.5.4 → Microsoft.Bcl.AsyncInterfaces/8.0.0 → Microsoft.Extensions.DependencyInjection.Abstractions/8.0.0 → System.Buffers/4.5.1 → System.Numerics.Vectors/4.4.0 → System.Memory/4.5.5 → Microsoft.Extensions.Logging.Abstractions/8.0.0

### Штатный граф NuGet из project.assets.json

- Microsoft.Bcl.AsyncInterfaces/8.0.0 → {'System.Threading.Tasks.Extensions': '4.5.4'}
- Microsoft.Extensions.DependencyInjection.Abstractions/8.0.0 → {'Microsoft.Bcl.AsyncInterfaces': '8.0.0', 'System.Threading.Tasks.Extensions': '4.5.4'}
- Microsoft.Extensions.Logging.Abstractions/8.0.0 → {'Microsoft.Extensions.DependencyInjection.Abstractions': '8.0.0', 'System.Buffers': '4.5.1', 'System.Memory': '4.5.5'}
- Microsoft.NETCore.Platforms/1.1.0 → нет зависимостей
- NETStandard.Library/2.0.3 → {'Microsoft.NETCore.Platforms': '1.1.0'}
- System.Buffers/4.5.1 → нет зависимостей
- System.Memory/4.5.5 → {'System.Buffers': '4.5.1', 'System.Numerics.Vectors': '4.4.0', 'System.Runtime.CompilerServices.Unsafe': '4.5.3'}
- System.Numerics.Vectors/4.4.0 → нет зависимостей
- System.Runtime.CompilerServices.Unsafe/4.5.3 → нет зависимостей
- System.Threading.Tasks.Extensions/4.5.4 → {'System.Runtime.CompilerServices.Unsafe': '4.5.3'}

### Сопоставление

NuGet объединяет ограничения версий и учитывает приоритет прямых зависимостей. Учебный DFS хранит узлы как пары имя и версия и выбирает минимальную версию отдельно для каждого ребра. Поэтому могут появиться две версии одного пакета. Также штатный restore добавляет NETStandard.Library для целевой платформы, а учебный граф начинается с пакета.
