# Auto-GAPS

## Getting started

1. Install the dependencies:

 - Python version: >= 3.9

```
pip install -r requirements.txt
```

2. Create the configuration file


```
cp config.toml.example config.toml
```
3. Modify the newly created file to add your switchaai credentials and hooks configuration.



4. Launch auto-gaps
```
python main.py
```

_You should schedule a task to execute auto-gaps_, see `cron` for linux or `taskschd` for windows. 

## Compatiblity

<table>
    <thead>
        <th>OS</th>
        <th>geckodriver</th>
        <th>chromedriver</th>
    </thead>
    <tr>
        <td>Windows 10 x64</td>
        <td style="text-align:center">✅</td>
        <td style="text-align:center">✅</td>
    </tr>
    <tr>
        <td>Centos 8 x86_64</td>
        <td style="text-align:center">✅</td>
        <td style="text-align:center">❌</td>
    </tr>
</table>
