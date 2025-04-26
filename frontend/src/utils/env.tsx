export function getEnvVar(name: string): string {
    const value = import.meta.env[name]

    if (!value) {
        throw new Error('Environment var ${name} is not defined!');
    }
    return value
}