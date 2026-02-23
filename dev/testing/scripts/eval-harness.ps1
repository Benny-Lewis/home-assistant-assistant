param(
    [ValidateSet('all', 'capability', 'regression')]
    [string]$Suite = 'all',
    [ValidateRange(1, 10)]
    [int]$Passes = 3,
    [string]$ReportPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
    $scriptDir = Split-Path -Parent $PSCommandPath
    return (Resolve-Path (Join-Path $scriptDir '..\..\..')).Path
}

function Load-CasesFromDir {
    param(
        [string]$DirectoryPath,
        [string]$SuiteName
    )

    if (-not (Test-Path -LiteralPath $DirectoryPath)) {
        return @()
    }

    $files = Get-ChildItem -LiteralPath $DirectoryPath -File -Filter *.json | Sort-Object Name
    $allCases = @()

    foreach ($file in $files) {
        $raw = Get-Content -LiteralPath $file.FullName -Raw
        $json = ConvertFrom-Json -InputObject $raw

        if ($null -eq $json.cases) {
            throw "Eval file '$($file.FullName)' is missing 'cases'."
        }

        foreach ($case in @($json.cases)) {
            if ([string]::IsNullOrWhiteSpace([string]$case.id) -or $null -eq $case.checks) {
                throw "Case in '$($file.FullName)' is missing required fields ('id', 'checks')."
            }

            $checks = @()
            foreach ($checkObject in @($case.checks)) {
                $checkHash = @{}
                if ($checkObject.PSObject.Properties.Name -contains 'path' -and $null -ne $checkObject.path) {
                    $checkHash.path = [string]$checkObject.path
                }
                if ($checkObject.PSObject.Properties.Name -contains 'contains' -and $null -ne $checkObject.contains) {
                    $checkHash.contains = [string]$checkObject.contains
                }
                if ($checkObject.PSObject.Properties.Name -contains 'not_contains' -and $null -ne $checkObject.not_contains) {
                    $checkHash.not_contains = [string]$checkObject.not_contains
                }
                $checks += $checkHash
            }

            $caseWithMeta = @{
                suite = $SuiteName
                source_file = $file.FullName
                id = [string]$case.id
                name = [string]$case.name
                description = [string]$case.description
                checks = $checks
            }

            $allCases += $caseWithMeta
        }
    }

    return $allCases
}

function Evaluate-Check {
    param(
        [hashtable]$Check,
        [string]$RepoRoot
    )

    if (-not $Check.ContainsKey('path')) {
        return @{
            passed = $false
            detail = "Missing 'path' in check."
        }
    }

    $relativePath = [string]$Check.path
    $absolutePath = Join-Path $RepoRoot $relativePath

    if (-not (Test-Path -LiteralPath $absolutePath)) {
        return @{
            passed = $false
            detail = "File not found: $relativePath"
        }
    }

    $content = Get-Content -LiteralPath $absolutePath -Raw

    if ($Check.ContainsKey('contains')) {
        $needle = [string]$Check.contains
        if ($content.Contains($needle)) {
            return @{
                passed = $true
                detail = "contains matched in $relativePath"
            }
        }

        return @{
            passed = $false
            detail = "expected content not found in ${relativePath}: $needle"
        }
    }

    if ($Check.ContainsKey('not_contains')) {
        $needle = [string]$Check.not_contains
        if ($content.Contains($needle)) {
            return @{
                passed = $false
                detail = "unexpected content found in ${relativePath}: $needle"
            }
        }

        return @{
            passed = $true
            detail = "not_contains matched in $relativePath"
        }
    }

    return @{
        passed = $false
        detail = "Check must define either 'contains' or 'not_contains'."
    }
}

function Evaluate-Case {
    param(
        [hashtable]$Case,
        [string]$RepoRoot
    )

    $checkResults = @()
    $allPassed = $true

    foreach ($check in $Case.checks) {
        $result = Evaluate-Check -Check $check -RepoRoot $RepoRoot
        $pathValue = ''
        $containsValue = ''
        $notContainsValue = ''
        if ($check.ContainsKey('path')) {
            $pathValue = [string]$check['path']
        }
        if ($check.ContainsKey('contains')) {
            $containsValue = [string]$check['contains']
        }
        if ($check.ContainsKey('not_contains')) {
            $notContainsValue = [string]$check['not_contains']
        }

        $checkResults += @{
            path = $pathValue
            contains = $containsValue
            not_contains = $notContainsValue
            passed = [bool]$result.passed
            detail = [string]$result.detail
        }

        if (-not $result.passed) {
            $allPassed = $false
        }
    }

    return @{
        passed = $allPassed
        checks = $checkResults
    }
}

$repoRoot = Get-RepoRoot
$capabilityDir = Join-Path $repoRoot 'dev\testing\evals\capability'
$regressionDir = Join-Path $repoRoot 'dev\testing\evals\regression'

$cases = @()
if ($Suite -eq 'all' -or $Suite -eq 'capability') {
    $cases += Load-CasesFromDir -DirectoryPath $capabilityDir -SuiteName 'capability'
}
if ($Suite -eq 'all' -or $Suite -eq 'regression') {
    $cases += Load-CasesFromDir -DirectoryPath $regressionDir -SuiteName 'regression'
}

if ($cases.Count -eq 0) {
    throw "No eval cases found for suite '$Suite'."
}

$caseRuns = @()
for ($attempt = 1; $attempt -le $Passes; $attempt++) {
    foreach ($case in $cases) {
        $evaluation = Evaluate-Case -Case $case -RepoRoot $repoRoot
        $caseRuns += [pscustomobject]@{
            attempt = $attempt
            suite = $case.suite
            id = $case.id
            name = $case.name
            passed = [bool]$evaluation.passed
            checks = $evaluation.checks
        }
    }
}

$grouped = $caseRuns | Group-Object -Property id
$summaryCases = @()
foreach ($group in $grouped) {
    $runs = @($group.Group | Sort-Object attempt)
    $singleRunPassed = [bool]$runs[0].passed
    $passAtKPassed = [bool](($runs | Where-Object { $_.passed }).Count -gt 0)

    $summaryCases += [pscustomobject]@{
        id = $runs[0].id
        suite = $runs[0].suite
        name = $runs[0].name
        single_run_passed = $singleRunPassed
        pass_at_k_passed = $passAtKPassed
        run_passes = @($runs | ForEach-Object { [bool]$_.passed })
    }
}

$totalCases = $summaryCases.Count
$singleRunPassCount = @($summaryCases | Where-Object { $_.single_run_passed }).Count
$passAtKPassCount = @($summaryCases | Where-Object { $_.pass_at_k_passed }).Count

$singleRunPassRate = [math]::Round(($singleRunPassCount / $totalCases) * 100, 2)
$passAtKRate = [math]::Round(($passAtKPassCount / $totalCases) * 100, 2)

Write-Host "Eval Harness"
Write-Host "Suite: $Suite"
Write-Host "Passes: $Passes"
Write-Host "Cases: $totalCases"
Write-Host "Single-run pass rate: $singleRunPassRate% ($singleRunPassCount/$totalCases)"
Write-Host "Pass@${Passes}: $passAtKRate% ($passAtKPassCount/$totalCases)"
Write-Host ""

$failingCases = @($summaryCases | Where-Object { -not $_.single_run_passed })
if ($failingCases.Count -gt 0) {
    Write-Host "Failing Cases (single-run):"
    foreach ($f in $failingCases) {
        Write-Host "- [$($f.suite)] $($f.id): $($f.name)"
    }
} else {
    Write-Host "All cases passed single-run."
}

if ($ReportPath -ne '') {
    $report = @{
        generated_at = (Get-Date).ToString('o')
        suite = $Suite
        passes = $Passes
        totals = @{
            cases = $totalCases
            single_run_pass_count = $singleRunPassCount
            single_run_pass_rate = $singleRunPassRate
            pass_at_k_pass_count = $passAtKPassCount
            pass_at_k_rate = $passAtKRate
        }
        cases = $summaryCases
        runs = $caseRuns
    }

    $reportDir = Split-Path -Parent $ReportPath
    if ($reportDir -and -not (Test-Path -LiteralPath $reportDir)) {
        New-Item -ItemType Directory -Path $reportDir | Out-Null
    }

    ($report | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $ReportPath -Encoding UTF8
    Write-Host "Report written to: $ReportPath"
}

if ($singleRunPassCount -ne $totalCases) {
    exit 1
}

exit 0
