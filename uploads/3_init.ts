import { environment } from '../environments/environment';
import { initApp } from '../dlv-ng-auth/shared/services/initApp';


export function init (): () => Promise<any> {
  return (): Promise<any> => {
      let authOption = Object.assign({}, environment.AUTH_CONFIG);
      return initApp(authOption)
  }
}
