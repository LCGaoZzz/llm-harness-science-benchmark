param([string]$Action, [string]$Round='01', [string]$Origin='derived', [string]$Note='')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$cli='C:\Users\Administrator\.codex\skills\scientific-organism\scripts\campaign-cli.exe'
function Invoke-Ledger($verb,$payload){
 $json=$payload | ConvertTo-Json -Depth 35 -Compress
 $raw=$json | & $cli --store (Join-Path $root '.campaign') --session 'earth-moon-12' $verb -
 if($LASTEXITCODE -ne 0){throw "Ledger call failed"}; $raw | Set-Content -LiteralPath (Join-Path $PSScriptRoot "ledger-$Round-$verb.json") -Encoding utf8
 $r=$raw | ConvertFrom-Json
 if($r.ok -eq $false){throw $raw}
 return $r
}
if($Action -eq 'record'){
 $r=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot "round-$Round.json") | ConvertFrom-Json
 $p=@{candidates=@(@{label="r$Round-$($r.method)-h$($r.h)";origin=$Origin;factors=@{integrator=$r.method;step="$($r.h)";regime='L4';duration='100'};metrics=@{log10_max_jacobi_drift=$r.log10_max_jacobi_drift;max_jacobi_drift=$r.maxDrift;passed_checks=$r.tests.passed;total_checks=$r.tests.total;elapsed_ms=$r.elapsed_ms};program="integrate(presets.l4.state, $($r.method), $($r.h), 100); sample max absolute Jacobi drift at every step; run selfTests()";program_ref=$r.artifact;artifact=$r.artifact;payload=@{initial='L4 + 0.01 x';T=100;cost='local CPU only; no paid API';evidence="verification/round-$Round.json"};protocol='Perturbed L4; T=100 TU; maximum absolute Jacobi drift sampled at every accepted fixed step; independent self-tests reported separately.'});design='controlled';note=$Note}
 $proposalPath=Join-Path $PSScriptRoot "ledger-$Round-propose.json"
 if(Test-Path -LiteralPath $proposalPath){$proposal=Get-Content -Raw -LiteralPath $proposalPath | ConvertFrom-Json;$pick=$proposal.picks[0];if($null -ne $pick.predicted){$p.candidates[0].predicted=$pick.predicted;$p.candidates[0].predicted_sd=$pick.predicted_sd}}
 $p.candidates[0].holes=@{h=@{value=$r.h;range=@(.000625,.02);scale='log'};integrator=@{level=$r.method;levels=@('rk4','yoshida')}}
 $out=Invoke-Ledger 'record' $p
 $out | Select-Object ok,round,should_stop,stop_reason,needs_new_theory,expansion_required,what_is_unexplained | ConvertTo-Json -Depth 8
 $s=Invoke-Ledger 'status' @{}
 $s | Select-Object should_stop,stop_reason,theories,calibration,covers_data,unexplained_results,origin_audit,space_looks_exhausted | ConvertTo-Json -Depth 10
}
elseif($Action -eq 'theories'){
 $p=@{theories=@(
 @{statement='At fixed step, symplectic Yoshida yields lower long-time Jacobi drift than RK4 on smooth L4 motion.';factors=@('integrator');contrasts=@(@{factor='integrator';level='yoshida';direction=-1});prediction='Yoshida has smaller maximum |C-C0| at T=100 for matched h.';origin='prior'},
 @{statement='At these finite horizons RK4 error constants dominate; RK4 beats Yoshida despite not being symplectic.';factors=@('integrator');contrasts=@(@{factor='integrator';level='rk4';direction=-1});prediction='RK4 has smaller maximum |C-C0| at T=100 for matched h.';origin='prior'},
 @{statement='Step size controls the dominant truncation error; halving h lowers drift before roundoff dominates.';factors=@('step');contrasts=@(@{factor='step';level='0.005';direction=-1},@{factor='step';level='0.02';direction=1});prediction='Smaller h improves drift for both schemes until a numerical floor.';origin='prior'}
 )}
 Invoke-Ledger 'theories' $p | ConvertTo-Json -Depth 10
 Invoke-Ledger 'status' @{} | ConvertTo-Json -Depth 10
}
elseif($Action -eq 'propose'){
 # Fixed, explicitly bounded numerical experiment pool; product validation proceeds alongside.
 $seen=@{};Get-ChildItem -LiteralPath $PSScriptRoot -Filter 'round-*.json' | ForEach-Object {$r=Get-Content -Raw $_.FullName | ConvertFrom-Json;$seen["$($r.method)|$($r.h)"]=$true}
 $pool=@();foreach($m in @('rk4','yoshida')){foreach($h in @('0.02','0.01','0.005','0.0025','0.00125','0.000625')){if(-not $seen.ContainsKey("$m|$h")){$pool+=@{label="$m|$h";factors=@{integrator=$m;step=$h;regime='L4';duration='100'}}}}}
 Invoke-Ledger 'propose' @{batch=1;pool=$pool;explore=1.0} | ConvertTo-Json -Depth 12
}
