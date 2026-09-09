# Science-only final audit — protocol fixed before added runs

Source commit: ac5a306be9b29978ad6787903821b4a6a181ff01. Entrants: gptweb_gpt-6pro, codex_6astra-xhigh, zcode_glm-5.3max (Windows), harnessL_ds-4.1flashmax.

Evidence used for new judgement: final original HTML, fresh computations by original kernels, independently computed physical quantities. Intermediate files, development history, screenshots, self-test counts, code length, algorithm counts, and UI quality earn no points. Existing audit results are checks, not score inputs. No source fixes.

Results-first categories (100): mathematical correctness 30; numerical result accuracy/convergence 35; physical demonstrations and quantitative claims 25; scientifically invalid-result control 10. Category weights and scores are reviewer choices, not empirical probabilities. Scores will be assigned after the numerical comparison. Basic correctness is not graded by sub-roundoff differences; verified algorithms get credit without requiring submitted proof logs. Lack of a full inertial-view implementation is not a scientific error when reported quantities are correct.

New common inputs, each using its own mu:
- L4: [0.51-mu, sqrt(3)/2, 0, 0], T=500, h=0.01 and 0.005.
- Earth: [0.18-mu, 0, 0, sqrt((1-mu)/0.18)-0.18], T=50, h=0.001 and 0.0005.
- Shared lunar flyby: [0.983023190751,0.339530631148,0.364091086118,-0.756469092483], T=0.8, h=0.0001 and 0.00005 (chosen from the existing Codex close-encounter preset, without parameter optimization). Physical relevance checked independently; it is not a universal scattering sample.

For each original fixed-step method evaluate final full state and maximum absolute Jacobi drift at accepted step endpoints, final accumulated Earth-relative phase for the Earth orbit, and finite-state/completion. Also exercise DS adaptive GBS at its original default k=5, Bulirsch sequence, rtol=1e-13, atol=1e-16, dt=0.001, and a tolerance-refined run (rtol=1e-14, atol=1e-17). DS has a different method/order and cost; these are capability/results comparisons, not matched cost or universal integrator rankings.

Independent references: DOP853 rotational equations plus an independently formulated moving-primary inertial integration. Reference refinement/differences explicitly recorded. Differences comparable to reference uncertainty not ranked. Previously identified unphysical extreme velocity crossing probes are sensitivity checks, not primary quality ranking.

Physical outputs independently checked: L4 linear-mode periods and actual perturbation motion, actual lunar flyby closest distances/times and assertions in final HTML, equal lunar-radius inbound/outbound speed/energy comparisons where available. Inertial speed is R(t)(vx-y,vy+x); translating to geocentric velocities requires subtracting Earth's motion. Finite-time trajectories do not prove arbitrary long-term stability. No preference for nominal symplecticity over independently superior non-symplectic accuracy.

## Post-primary sensitivity check
After the primary results, an additional Earth RK4 check at h=1e-4 and 5e-5 was added for ALL four submissions. Its purpose is to avoid falsely inferring that only DS can reach high accuracy. The supplementary experiment was not in the original protocol. It confirms that all four can obtain high-accuracy results with sufficiently small steps. Numeric differences at the reference/roundoff floor are not ranked. All four outcomes are retained in refinement_check.json.
