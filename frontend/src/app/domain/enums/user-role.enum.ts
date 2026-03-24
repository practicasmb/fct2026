// TODO: Integrate UserRole enum with AuthUser.role field for type safety when role management is implemented
export enum UserRole {
  Administrator = 'administrator', // backend returns 'administrator' - required for compatibility
  User = 'user',
}
