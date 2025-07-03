import type { Config } from 'jest';
import { pathsToModuleNameMapper } from 'ts-jest';
const { compilerOptions } = require('./tsconfig.json');
const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleNameMapper: pathsToModuleNameMapper(compilerOptions.paths ?? {}, { prefix: '<rootDir>/' }),
  transform: {
    '^.+\\.[tj]sx?$': [
      'ts-jest',
      {
        diagnostics: { ignoreCodes: [1343, 2345, 2339, 2322] }, // Ignore TypeScript errors
        astTransformers: {
          before: [
            {
              path: 'ts-jest-mock-import-meta',
              options: {
                metaObjectReplacement: {
                  env: {
                    VITE_API_URL: 'http://localhost:3000'
                    // Puedes agregar otras variables de entorno aquí
                  }
                }
              }
            }
          ]
        }
      }
    ]
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
};

export default config;
