# this is a standalone script that automatically searches through the drivers for any vulnerable versions
# consider using wmic / driverquery / Get-WmiObject / Get-PnpDevice / Get-WindowsDriver / 

# needs the powershell.exe -ep bypass 
# wmic os get BuildNumber,version

$osInfo = Get-WmiObject Win32_OperatingSystem;
$buildNumber = $osInfo.BuildNumber;
$version = $osInfo.Version;

# Get all drivers on the system
$drivers = Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.DeviceClass -eq 'MEDIA' -or $_.DeviceClass -eq 'DISPLAY' }

# Display information for each driver
foreach ($driver in $drivers) {
    $version = $driver.DriverVersion;
    $driverName = $driver.DriverName;
    Write-Host "Build Number: $buildNumber"
    Write-Host "Driver Version: $version"
    Write-Host "Driver Name:  $driverName"
    Write-Host "----------------------------------------"
}

$cvearray = @(
    @{
        "cve" = ""

    }
);


