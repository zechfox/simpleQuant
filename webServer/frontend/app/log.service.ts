import {Injectable} from '@angular/core';
import {Observable, Subject} from 'rxjs/Rx';
import {WebSocketService} from './websocket.service';

const logServerUrl:string = 'ws://' + window.location.hostname + (window.location.port ? ':' + window.location.port: '') + '/logServer';

export interface LogMessage {
    name: string;
    message: string;
}

@Injectable()
export class LogService {
  public logMessages: Subject<LogMessage>;

  constructor(wsService: WebSocketService) {

    this.logMessages = <Subject<LogMessage>>wsService
        .connect(logServerUrl)
	.map((response: MessageEvent): LogMessage => {
	  let data = JSON.parse(response.data);
	  return {
	    name: data.name,
	    message: data.message,
	  }
	});
  }
 
}
