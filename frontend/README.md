# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.


## Visual realism update

The dashboard includes an optional broadcast-style cyclone vortex at the observed peak-intensity center. It uses the real IBTrACS peak wind and pressure as labels and animates a counter-clockwise circulation around that observed center. The vortex is a visualization aid, not a measured wind-vector field or official wind-radius product; IBTrACS position/intensity observations are the underlying evidence.

The flood pipeline is also defensive against empty cloud-filtered Dynamic World windows: it checks scene availability, uses widened real event windows when needed, and combines the result with Sentinel-1 SAR change and a persistent-water mask.


## Meteorological Wind Visualization

The dashboard renders a full-map ERA5 environmental wind field with animated streamlines. Along the complete IBTrACS track, a geographically bounded derived intensity envelope uses observed WMO wind values to color the storm corridor from low to extreme intensity. This envelope is a visualization aid and is not an official measured wind-radius product.
